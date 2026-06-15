import copy
import math
import random
from typing import Dict, List, Tuple, Any, Set, Optional

from quantum.optimization.hardware_cost_model import (
    DEFAULT_T1_SEC,
    DEFAULT_T2_SEC,
    estimate_swap_duration,
    get_gate_properties,
    get_qubit_quality,
)

class AdvancedRouter:
    """
    Implements advanced layout routing algorithms to satisfy physical coupling map 
    constraints with minimal SWAP gate overhead and critical path depth.
    """
    def __init__(self, coupling_map: Optional[List[Tuple[int, int]]], backend: Optional[Any] = None):
        self.backend = backend
        if coupling_map is None and backend is not None and getattr(backend, "coupling_map", None) is not None:
            coupling_map = list(backend.coupling_map)
        self.coupling_map = coupling_map or []
        if self.coupling_map:
            self.num_physical = max(max(edge) for edge in coupling_map) + 1
            if backend is not None and getattr(backend, "num_qubits", None):
                self.num_physical = max(self.num_physical, backend.num_qubits)
            self.edges = set()
            for edge in self.coupling_map:
                u, v = int(edge[0]), int(edge[1])
                self.edges.add((u, v))
                self.edges.add((v, u))
        else:
            self.num_physical = 0
            self.edges = set()
            
        self.dist_matrix = self._compute_all_pairs_shortest_paths()

    def compute_optimal_weights(self, circuit_depth: int, num_qubits: int, backend: Optional[Any]) -> Tuple[float, float]:
        t2_values = []
        num_phys = num_qubits
        if backend:
            if hasattr(backend, "num_qubits"):
                num_phys = backend.num_qubits
            elif hasattr(backend, "configuration"):
                try:
                    num_phys = backend.configuration().n_qubits
                except Exception:
                    pass
        for q in range(min(num_qubits, num_phys)):
            try:
                props = backend.qubit_properties(q)
                if props and props.t2:
                    t2_values.append(props.t2)
            except Exception:
                pass
        
        avg_t2 = sum(t2_values) / len(t2_values) if t2_values else 90e-6
        
        # Para circuitos poco profundos (depth < 30), 
        # priorizar reducción de puertas sobre coherencia
        if circuit_depth < 30:
            w_d = 0.8   # Alto peso a distancia (menos SWAPs)
            w_c = 0.2   # Bajo peso a coherencia
        # Para circuitos medianos (depth 30-100),
        # balance entre puertas y coherencia
        elif circuit_depth < 100:
            w_d = 0.6
            w_c = 0.4
        # Para circuitos profundos (depth > 100),
        # priorizar coherencia
        else:
            w_d = 0.4
            w_c = 0.6
        
        return w_d, w_c

    def _compute_all_pairs_shortest_paths(self) -> Dict[int, Dict[int, int]]:
        if self.num_physical == 0:
            return {}
        dist = {i: {j: 9999 for j in range(self.num_physical)} for i in range(self.num_physical)}
        for i in range(self.num_physical):
            dist[i][i] = 0
            for neighbor in range(self.num_physical):
                if (i, neighbor) in self.edges:
                    dist[i][neighbor] = 1
                    
        # Floyd-Warshall
        for k in range(self.num_physical):
            for i in range(self.num_physical):
                for j in range(self.num_physical):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
        return dist

    def route(self, qade_json: Dict[str, Any], method: str = "sabre", initial_layout: Optional[Dict[int, int]] = None) -> Tuple[Dict[str, Any], Dict[int, int]]:
        """
        Routes the circuit using the specified method.
        Returns:
            Tuple[routed_circuit_json, final_layout_dict]
        """
        if not self.coupling_map:
            return qade_json, {i: i for i in range(qade_json.get("qubits", 0))}
            
        num_logical = qade_json.get("qubits", 0)
        
        # Setup initial layout (virtual -> physical)
        if initial_layout is not None:
            v_to_p = initial_layout.copy()
        else:
            v_to_p = {i: i for i in range(num_logical)}
            
        # Ensure it is a full bijection to all physical qubits
        p_to_v = {p: v for v, p in v_to_p.items()}
        used_phys = set(p_to_v.keys())
        used_virt = set(p_to_v.values())
        all_phys = set(range(self.num_physical))
        all_virt = set(range(max(num_logical, self.num_physical)))
        
        rem_phys = sorted(list(all_phys - used_phys))
        rem_virt = sorted(list(all_virt - used_virt))
        for p, v in zip(rem_phys, rem_virt):
            v_to_p[v] = p
            p_to_v[p] = v
            
        # Estimate depth to compute optimal weights
        gates_list = qade_json.get("gates", [])
        q_depth = {}
        for g in gates_list:
            for q in g.get("qubits", []):
                q_depth[q] = q_depth.get(q, 0) + 1
        est_depth = max(q_depth.values()) if q_depth else 0
        w_d, w_c = self.compute_optimal_weights(est_depth, num_logical, self.backend)

        try:
            if method == "sabre":
                return self._route_sabre(qade_json, v_to_p, p_to_v)
            elif method in ("coherence_aware_sabre", "coherence-aware-sabre", "hardware_aware_sabre"):
                return self._route_coherence_aware_sabre(qade_json, v_to_p, p_to_v, alpha=w_d, delta=w_c)
            elif method == "astar":
                return self._route_astar(qade_json, v_to_p, p_to_v)
            elif method == "beam":
                return self._route_beam_search(qade_json, v_to_p, p_to_v)
            elif method == "simulated_annealing":
                return self._route_simulated_annealing(qade_json, v_to_p, p_to_v)
            elif method == "evolutionary":
                return self._route_evolutionary(qade_json, v_to_p, p_to_v)
            elif method == "hybrid":
                return self._route_hybrid(qade_json, v_to_p, p_to_v)
            else:
                # Default fallback to classic BFS route (returning identity layout)
                from quantum.evolution.evolution_engine import route_circuit
                res = route_circuit(qade_json, self.coupling_map)
                return res, {i: i for i in range(self.num_physical)}
        except Exception as e:
            from quantum.evolution.evolution_engine import route_circuit
            res = route_circuit(qade_json, self.coupling_map)
            return res, {i: i for i in range(self.num_physical)}

    def _gate_duration(self, gate_type: str, qargs: Tuple[int, ...]) -> float:
        if self.backend is None:
            if len(qargs) == 2:
                return 300e-9
            if gate_type.upper() == "RZ":
                return 0.0
            return 50e-9
        return get_gate_properties(self.backend, gate_type, qargs)["duration"]

    def _swap_duration(self, edge: Tuple[int, int]) -> float:
        if self.backend is None:
            return 900e-9
        return estimate_swap_duration(self.backend, edge)

    def _coherence_loss(self, physical_qubits: Set[int], extra_duration: float) -> float:
        if extra_duration <= 0:
            return 0.0
        loss = 0.0
        for qubit in physical_qubits:
            if self.backend is not None:
                quality = get_qubit_quality(self.backend, qubit)
                t1 = max(quality["t1"], 1e-15)
                t2 = max(quality["t2"], 1e-15)
            else:
                t1 = DEFAULT_T1_SEC
                t2 = DEFAULT_T2_SEC
            loss += extra_duration / t1 + extra_duration / t2
        return loss

    def _route_coherence_aware_sabre(
        self,
        qade_json: Dict[str, Any],
        v_to_p: Dict[int, int],
        p_to_v: Dict[int, int],
        alpha: float = 1.0,
        beta: float = 0.2,
        gamma: float = 0.05,
        delta: float = 2.0,
    ) -> Tuple[Dict[str, Any], Dict[int, int]]:
        """SABRE variant minimizing distance, SWAPs, duration, and T1/T2 loss."""
        gates = qade_json.get("gates", [])
        gate_parents = {i: set() for i in range(len(gates))}
        gate_children = {i: set() for i in range(len(gates))}
        qubit_last_gate = {}

        for i, g in enumerate(gates):
            for qubit in g.get("qubits", []):
                if qubit in qubit_last_gate:
                    parent_idx = qubit_last_gate[qubit]
                    gate_parents[i].add(parent_idx)
                    gate_children[parent_idx].add(i)
                qubit_last_gate[qubit] = i

        front_layer = {i for i in range(len(gates)) if not gate_parents[i]}
        pending_parents = {i: len(gate_parents[i]) for i in range(len(gates))}
        routed_gates = []
        qubit_end_times = {p: 0.0 for p in range(self.num_physical)}
        lookahead_weight = 0.5
        last_swap = None
        swap_count = 0
        consecutive_swaps = 0
        max_consecutive_swaps = max(100, self.num_physical * 4)

        while front_layer:
            executed_any = True
            while executed_any:
                executed_any = False
                to_execute = []
                for idx in front_layer:
                    gate = gates[idx]
                    q = gate.get("qubits", [])
                    if len(q) == 1:
                        to_execute.append(idx)
                    elif len(q) == 2:
                        p0 = v_to_p[q[0]]
                        p1 = v_to_p[q[1]]
                        if (p0, p1) in self.edges:
                            to_execute.append(idx)

                if to_execute:
                    executed_any = True
                    consecutive_swaps = 0
                    for idx in to_execute:
                        front_layer.remove(idx)
                        mapped_gate = gates[idx].copy()
                        mapped_gate["qubits"] = [
                            v_to_p[qubit] for qubit in gates[idx]["qubits"]
                        ]
                        routed_gates.append(mapped_gate)

                        qargs = tuple(mapped_gate["qubits"])
                        duration = self._gate_duration(mapped_gate.get("type", ""), qargs)
                        if qargs:
                            start = max(qubit_end_times.get(q, 0.0) for q in qargs)
                            finish = start + duration
                            for q in qargs:
                                qubit_end_times[q] = finish

                        for child in gate_children[idx]:
                            pending_parents[child] -= 1
                            if pending_parents[child] == 0:
                                front_layer.add(child)

            if not front_layer:
                break

            front_qubits_phys = set()
            for idx in front_layer:
                for q in gates[idx].get("qubits", []):
                    front_qubits_phys.add(v_to_p[q])

            candidate_swaps = [
                (u, v)
                for u, v in self.edges
                if u < v and (u in front_qubits_phys or v in front_qubits_phys)
            ]
            if not candidate_swaps:
                break

            lookahead_layer = []
            visited = set(front_layer)
            queue = list(front_layer)
            while queue and len(lookahead_layer) < 20:
                curr = queue.pop(0)
                for child in gate_children[curr]:
                    if child not in visited:
                        visited.add(child)
                        lookahead_layer.append(child)
                        queue.append(child)

            best_swap = None
            best_cost = float("inf")
            for u, v in candidate_swaps:
                if last_swap in ((u, v), (v, u)) and len(candidate_swaps) > 1:
                    continue

                v_u = p_to_v[u]
                v_v = p_to_v[v]
                sim_v_to_p = v_to_p.copy()
                sim_v_to_p[v_u] = v
                sim_v_to_p[v_v] = u

                front_distance = 0.0
                expected_duration = self._swap_duration((u, v))
                impacted_qubits = {u, v}
                for idx in front_layer:
                    q = gates[idx].get("qubits", [])
                    if len(q) == 2:
                        p0 = sim_v_to_p[q[0]]
                        p1 = sim_v_to_p[q[1]]
                        front_distance += self.dist_matrix[p0][p1]
                        expected_duration += self._gate_duration(
                            gates[idx].get("type", ""), (p0, p1)
                        )
                        impacted_qubits.update((p0, p1))

                look_distance = 0.0
                for idx in lookahead_layer:
                    q = gates[idx].get("qubits", [])
                    if len(q) == 2:
                        p0 = sim_v_to_p[q[0]]
                        p1 = sim_v_to_p[q[1]]
                        look_distance += self.dist_matrix[p0][p1]

                coherence_loss = self._coherence_loss(impacted_qubits, expected_duration)
                duration_us = expected_duration * 1e6
                cost = (
                    alpha * (front_distance + lookahead_weight * look_distance)
                    + beta * (swap_count + 1)
                    + gamma * duration_us
                    + delta * coherence_loss
                )
                if cost < best_cost:
                    best_cost = cost
                    best_swap = (u, v)

            if best_swap is None:
                break

            u, v = best_swap
            consecutive_swaps += 1
            if consecutive_swaps > max_consecutive_swaps:
                raise RuntimeError("Coherence-aware SABRE infinite loop detected")

            routed_gates.append({"type": "SWAP", "qubits": [u, v]})
            duration = self._swap_duration((u, v))
            start = max(qubit_end_times.get(u, 0.0), qubit_end_times.get(v, 0.0))
            finish = start + duration
            qubit_end_times[u] = finish
            qubit_end_times[v] = finish

            v_u = p_to_v[u]
            v_v = p_to_v[v]
            v_to_p[v_u] = v
            v_to_p[v_v] = u
            p_to_v[u] = v_v
            p_to_v[v] = v_u
            swap_count += 1
            last_swap = (u, v)

        return {"qubits": self.num_physical, "gates": routed_gates}, v_to_p

    def _route_sabre(self, qade_json: Dict[str, Any], v_to_p: Dict[int, int], p_to_v: Dict[int, int]) -> Tuple[Dict[str, Any], Dict[int, int]]:
        """SWAP-Aware Bypassing Recurrent Ejection (SABRE) look-ahead router."""
        gates = qade_json.get("gates", [])
        
        # Build DAG structure
        gate_parents = {i: set() for i in range(len(gates))}
        gate_children = {i: set() for i in range(len(gates))}
        qubit_last_gate = {}
        
        for i, g in enumerate(gates):
            q_list = g.get("qubits", [])
            for qubit in q_list:
                if qubit in qubit_last_gate:
                    parent_idx = qubit_last_gate[qubit]
                    gate_parents[i].add(parent_idx)
                    gate_children[parent_idx].add(i)
                qubit_last_gate[qubit] = i
                
        # Initialize front layer (gates with no parents)
        front_layer = set()
        pending_parents = {i: len(gate_parents[i]) for i in range(len(gates))}
        for i in range(len(gates)):
            if pending_parents[i] == 0:
                front_layer.add(i)
                
        routed_gates = []
        decay = {p: 1.0 for p in range(self.num_physical)}
        lookahead_weight = 0.5
        
        # Keep track of last SWAP to prevent infinite back-and-forth loops
        last_swap = None
        consecutive_swaps = 0
        max_consecutive_swaps = max(100, self.num_physical * 3)
        
        while front_layer:
            # 1. Execute all gates in the front layer that are currently adjacent
            executed_any = True
            while executed_any:
                executed_any = False
                to_execute = []
                for idx in front_layer:
                    gate = gates[idx]
                    q = gate.get("qubits", [])
                    if len(q) == 1:
                        to_execute.append(idx)
                    elif len(q) == 2:
                        p0 = v_to_p[q[0]]
                        p1 = v_to_p[q[1]]
                        if (p0, p1) in self.edges:
                            to_execute.append(idx)
                            
                if to_execute:
                    executed_any = True
                    consecutive_swaps = 0
                    for idx in to_execute:
                        front_layer.remove(idx)
                        # Add gate to output with mapped physical qubits
                        mapped_gate = gates[idx].copy()
                        mapped_gate["qubits"] = [v_to_p[qubit] for qubit in gates[idx]["qubits"]]
                        routed_gates.append(mapped_gate)
                        
                        # Update children
                        for child in gate_children[idx]:
                            pending_parents[child] -= 1
                            if pending_parents[child] == 0:
                                front_layer.add(child)
                                
            if not front_layer:
                break
                
            # 2. No gate in front layer is adjacent. We must select and apply a SWAP gate.
            # Candidate SWAPs are physical edges that contain at least one qubit in the front layer
            front_qubits_phys = set()
            for idx in front_layer:
                for q in gates[idx].get("qubits", []):
                    front_qubits_phys.add(v_to_p[q])
                    
            candidate_swaps = []
            for u, v in self.edges:
                if u < v and (u in front_qubits_phys or v in front_qubits_phys):
                    candidate_swaps.append((u, v))
                    
            if not candidate_swaps:
                # If no candidate swaps found (e.g. disconnected graphs), apply fallback
                break
                
            # Compute SABRE look-ahead cost for each candidate SWAP
            best_swap = None
            best_cost = 999999
            
            # Find look-ahead layer (descendants of front layer up to 20 gates)
            lookahead_layer = []
            visited = set(front_layer)
            queue = list(front_layer)
            while queue and len(lookahead_layer) < 20:
                curr = queue.pop(0)
                for child in gate_children[curr]:
                    if child not in visited:
                        visited.add(child)
                        lookahead_layer.append(child)
                        queue.append(child)
                        
            for u, v in candidate_swaps:
                # Skip reversing the immediate last SWAP to prevent lockups
                if last_swap == (u, v) or last_swap == (v, u):
                    if len(candidate_swaps) > 1:
                        continue
                
                # Simulate SWAP: Swap physical positions of the virtual qubits residing at u and v
                v_u = p_to_v[u]
                v_v = p_to_v[v]
                
                # Test cost after swap
                sim_v_to_p = v_to_p.copy()
                sim_v_to_p[v_u] = v
                sim_v_to_p[v_v] = u
                
                # Front layer cost
                front_cost = 0
                for idx in front_layer:
                    g = gates[idx]
                    q = g.get("qubits", [])
                    if len(q) == 2:
                        p0 = sim_v_to_p[q[0]]
                        p1 = sim_v_to_p[q[1]]
                        front_cost += self.dist_matrix[p0][p1] * max(decay[p0], decay[p1])
                        
                # Look-ahead cost
                look_cost = 0
                for idx in lookahead_layer:
                    g = gates[idx]
                    q = g.get("qubits", [])
                    if len(q) == 2:
                        p0 = sim_v_to_p[q[0]]
                        p1 = sim_v_to_p[q[1]]
                        look_cost += self.dist_matrix[p0][p1] * max(decay[p0], decay[p1])
                        
                total_cost = front_cost + lookahead_weight * look_cost
                
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_swap = (u, v)
                    
            if best_swap:
                u, v = best_swap
                consecutive_swaps += 1
                if consecutive_swaps > max_consecutive_swaps:
                    raise RuntimeError("SABRE infinite loop detected")
                # Apply SWAP
                routed_gates.append({"type": "SWAP", "qubits": [u, v]})
                v_u = p_to_v[u]
                v_v = p_to_v[v]
                
                v_to_p[v_u] = v
                v_to_p[v_v] = u
                p_to_v[u] = v_v
                p_to_v[v] = v_u
                
                # Update decays to prevent lockups
                decay[u] += 0.1
                decay[v] += 0.1
                for p in range(self.num_physical):
                    decay[p] = max(1.0, decay[p] - 0.01)
                    
                last_swap = (u, v)
            else:
                break
                
        # Return physical size circuit
        return {"qubits": self.num_physical, "gates": routed_gates}, v_to_p

    def _route_astar(self, qade_json: Dict[str, Any], v_to_p: Dict[int, int], p_to_v: Dict[int, int]) -> Tuple[Dict[str, Any], Dict[int, int]]:
        """Routes gates sequentially using A* pathfinding on the physical graph."""
        gates = qade_json.get("gates", [])
        routed_gates = []
        
        for gate in gates:
            q = gate.get("qubits", [])
            if len(q) == 1:
                routed_gates.append({"type": gate["type"], "qubits": [v_to_p[q[0]]]})
            elif len(q) == 2:
                # Find path to bring v_to_p[q[0]] adjacent to v_to_p[q[1]]
                p0 = v_to_p[q[0]]
                p1 = v_to_p[q[1]]
                
                if (p0, p1) in self.edges:
                    routed_gates.append({"type": gate["type"], "qubits": [p0, p1]})
                    continue
                    
                # Run A* to find path on coupling map
                path = self._find_astar_path(p0, p1)
                
                # Apply SWAPs along path (moves p0 toward p1)
                for i in range(len(path) - 2):
                    u = path[i]
                    v = path[i+1]
                    routed_gates.append({"type": "SWAP", "qubits": [u, v]})
                    
                    # Swap physical mapping
                    v_u = p_to_v[u]
                    v_v = p_to_v[v]
                    v_to_p[v_u] = v
                    v_to_p[v_v] = u
                    p_to_v[u] = v_v
                    p_to_v[v] = v_u
                    
                # Qubits are now adjacent! Execute target gate on final physical locations
                u_final = path[-2]
                v_final = path[-1]
                
                mapped_gate = gate.copy()
                mapped_gate["qubits"] = [u_final, v_final]
                routed_gates.append(mapped_gate)
                
        return {"qubits": self.num_physical, "gates": routed_gates}, v_to_p

    def _find_astar_path(self, start: int, end: int) -> List[int]:
        # Simple A* search for a single path between two physical nodes
        # Priority queue elements: (f_score, g_score, path)
        open_set = [(self.dist_matrix[start][end], 0, [start])]
        visited = set()
        
        while open_set:
            open_set.sort(key=lambda x: x[0])
            f, g, path = open_set.pop(0)
            node = path[-1]
            
            if node == end:
                return path
                
            if node in visited:
                continue
            visited.add(node)
            
            for neighbor in range(self.num_physical):
                if (node, neighbor) in self.edges and neighbor not in visited:
                    new_g = g + 1
                    new_f = new_g + self.dist_matrix[neighbor][end]
                    open_set.append((new_f, new_g, path + [neighbor]))
        return [start, end]

    def _route_beam_search(self, qade_json: Dict[str, Any], v_to_p: Dict[int, int], p_to_v: Dict[int, int], beam_width: int = 4) -> Tuple[Dict[str, Any], Dict[int, int]]:
        """Sequential routing using a limited-width Beam Search for SWAP selection."""
        gates = qade_json.get("gates", [])
        routed_gates = []
        
        for gate in gates:
            q = gate.get("qubits", [])
            if len(q) == 1:
                routed_gates.append({"type": gate["type"], "qubits": [v_to_p[q[0]]]})
            elif len(q) == 2:
                p0 = v_to_p[q[0]]
                p1 = v_to_p[q[1]]
                
                if (p0, p1) in self.edges:
                    routed_gates.append({"type": gate["type"], "qubits": [p0, p1]})
                    continue
                    
                # Beam search to find a short SWAP sequence
                # Queue elements: (heuristic_cost, path, current_v_to_p, current_p_to_v)
                queue = [(self.dist_matrix[p0][p1], [], v_to_p.copy(), p_to_v.copy())]
                
                best_swaps = None
                found = False
                
                for step in range(10): # Max 10 steps to prevent hangs
                    next_queue = []
                    for h, swaps, curr_v, curr_p in queue:
                        curr_p0 = curr_v[q[0]]
                        curr_p1 = curr_v[q[1]]
                        
                        if (curr_p0, curr_p1) in self.edges:
                            best_swaps = swaps
                            found = True
                            break
                            
                        # Generate neighbor states by applying a single SWAP
                        # Candidate swaps share at least one qubit with the target gate
                        for u, v in self.edges:
                            if u < v and (u in (curr_p0, curr_p1) or v in (curr_p0, curr_p1)):
                                sim_v = curr_v.copy()
                                sim_p = curr_p.copy()
                                v_u = sim_p[u]
                                v_v = sim_p[v]
                                sim_v[v_u] = v
                                sim_v[v_v] = u
                                sim_p[u] = v_v
                                sim_p[v] = v_u
                                
                                new_h = self.dist_matrix[sim_v[q[0]]][sim_v[q[1]]] + len(swaps) + 1
                                next_queue.append((new_h, swaps + [(u, v)], sim_v, sim_p))
                                
                    if found:
                        break
                        
                    # Filter top B candidates (Beam Width)
                    next_queue.sort(key=lambda x: x[0])
                    queue = next_queue[:beam_width]
                    
                # Apply chosen swaps
                if best_swaps:
                    for u, v in best_swaps:
                        routed_gates.append({"type": "SWAP", "qubits": [u, v]})
                        v_u = p_to_v[u]
                        v_v = p_to_v[v]
                        v_to_p[v_u] = v
                        v_to_p[v_v] = u
                        p_to_v[u] = v_v
                        p_to_v[v] = v_u
                        
                # Execute gate
                mapped_gate = gate.copy()
                mapped_gate["qubits"] = [v_to_p[q[0]], v_to_p[q[1]]]
                routed_gates.append(mapped_gate)
                
        return {"qubits": self.num_physical, "gates": routed_gates}, v_to_p

    def _route_simulated_annealing(self, qade_json: Dict[str, Any], v_to_p: Dict[int, int], p_to_v: Dict[int, int]) -> Tuple[Dict[str, Any], Dict[int, int]]:
        """Simulated Annealing wrapper over SABRE, optimizing look-ahead weights."""
        best_circuit = None
        best_swaps = 999999
        best_layout = None
        
        # Sweep lookahead weights
        temp = 1.0
        cooling_rate = 0.8
        curr_weight = 0.5
        
        for i in range(5):
            # Evaluate current weight
            routed, final_layout = self._route_sabre_with_weight(qade_json, v_to_p, p_to_v, curr_weight)
            swaps = sum(1 for g in routed["gates"] if g["type"] == "SWAP")
            
            if swaps < best_swaps:
                best_swaps = swaps
                best_circuit = routed
                best_layout = final_layout
                
            # Randomly perturb weight
            new_weight = max(0.0, min(1.0, curr_weight + random.uniform(-0.2, 0.2)))
            new_routed, _ = self._route_sabre_with_weight(qade_json, v_to_p, p_to_v, new_weight)
            new_swaps = sum(1 for g in new_routed["gates"] if g["type"] == "SWAP")
            
            # Acceptance probability
            if new_swaps < swaps or math.exp((swaps - new_swaps) / temp) > random.random():
                curr_weight = new_weight
                
            temp *= cooling_rate
            
        return best_circuit or qade_json, best_layout or v_to_p

    def _route_sabre_with_weight(self, qade_json: Dict[str, Any], v_to_p: Dict[int, int], p_to_v: Dict[int, int], weight: float) -> Tuple[Dict[str, Any], Dict[int, int]]:
        # Helper to run SABRE with a specific look-ahead weight
        # Copy states to avoid modifying original layout references
        sim_v = v_to_p.copy()
        sim_p = p_to_v.copy()
        
        gates = qade_json.get("gates", [])
        gate_parents = {i: set() for i in range(len(gates))}
        gate_children = {i: set() for i in range(len(gates))}
        qubit_last_gate = {}
        for i, g in enumerate(gates):
            for qubit in g.get("qubits", []):
                if qubit in qubit_last_gate:
                    parent_idx = qubit_last_gate[qubit]
                    gate_parents[i].add(parent_idx)
                    gate_children[parent_idx].add(i)
                qubit_last_gate[qubit] = i
        front_layer = set()
        pending_parents = {i: len(gate_parents[i]) for i in range(len(gates))}
        for i in range(len(gates)):
            if pending_parents[i] == 0:
                front_layer.add(i)
        routed_gates = []
        decay = {p: 1.0 for p in range(self.num_physical)}
        last_swap = None
        consecutive_swaps = 0
        max_consecutive_swaps = max(100, self.num_physical * 3)
        
        while front_layer:
            executed_any = True
            while executed_any:
                executed_any = False
                to_execute = []
                for idx in front_layer:
                    gate = gates[idx]
                    q = gate.get("qubits", [])
                    if len(q) == 1:
                        to_execute.append(idx)
                    elif len(q) == 2:
                        p0 = sim_v[q[0]]
                        p1 = sim_v[q[1]]
                        if (p0, p1) in self.edges:
                            to_execute.append(idx)
                if to_execute:
                    executed_any = True
                    consecutive_swaps = 0
                    for idx in to_execute:
                        front_layer.remove(idx)
                        mapped_gate = gates[idx].copy()
                        mapped_gate["qubits"] = [sim_v[qubit] for qubit in gates[idx]["qubits"]]
                        routed_gates.append(mapped_gate)
                        for child in gate_children[idx]:
                            pending_parents[child] -= 1
                            if pending_parents[child] == 0:
                                front_layer.add(child)
            if not front_layer:
                break
            front_qubits_phys = set()
            for idx in front_layer:
                for q in gates[idx].get("qubits", []):
                    front_qubits_phys.add(sim_v[q])
            candidate_swaps = []
            for u, v in self.edges:
                if u < v and (u in front_qubits_phys or v in front_qubits_phys):
                    candidate_swaps.append((u, v))
            if not candidate_swaps:
                break
            best_swap = None
            best_cost = 999999
            lookahead_layer = []
            visited = set(front_layer)
            queue = list(front_layer)
            while queue and len(lookahead_layer) < 20:
                curr = queue.pop(0)
                for child in gate_children[curr]:
                    if child not in visited:
                        visited.add(child)
                        lookahead_layer.append(child)
                        queue.append(child)
            for u, v in candidate_swaps:
                if last_swap == (u, v) or last_swap == (v, u):
                    if len(candidate_swaps) > 1:
                        continue
                v_u = sim_p[u]
                v_v = sim_p[v]
                sim_v_to_p = sim_v.copy()
                sim_v_to_p[v_u] = v
                sim_v_to_p[v_v] = u
                front_cost = 0
                for idx in front_layer:
                    g = gates[idx]
                    q = g.get("qubits", [])
                    if len(q) == 2:
                        p0 = sim_v_to_p[q[0]]
                        p1 = sim_v_to_p[q[1]]
                        front_cost += self.dist_matrix[p0][p1] * max(decay[p0], decay[p1])
                look_cost = 0
                for idx in lookahead_layer:
                    g = gates[idx]
                    q = g.get("qubits", [])
                    if len(q) == 2:
                        p0 = sim_v_to_p[q[0]]
                        p1 = sim_v_to_p[q[1]]
                        look_cost += self.dist_matrix[p0][p1] * max(decay[p0], decay[p1])
                total_cost = front_cost + weight * look_cost
                if total_cost < best_cost:
                    best_cost = total_cost
                    best_swap = (u, v)
            if best_swap:
                u, v = best_swap
                consecutive_swaps += 1
                if consecutive_swaps > max_consecutive_swaps:
                    raise RuntimeError("SABRE infinite loop detected")
                routed_gates.append({"type": "SWAP", "qubits": [u, v]})
                v_u = sim_p[u]
                v_v = sim_p[v]
                sim_v[v_u] = v
                sim_v[v_v] = u
                sim_p[u] = v_v
                sim_p[v] = v_u
                decay[u] += 0.1
                decay[v] += 0.1
                last_swap = (u, v)
            else:
                break
        return {"qubits": self.num_physical, "gates": routed_gates}, sim_v

    def _route_evolutionary(self, qade_json: Dict[str, Any], v_to_p: Dict[int, int], p_to_v: Dict[int, int]) -> Tuple[Dict[str, Any], Dict[int, int]]:
        """Evolutionary algorithm evaluating different initial layouts and selection weights."""
        # Simple genetic selection over 4 runs
        layouts = [
            v_to_p,
            {i: (i + 1) % self.num_physical for i in range(qade_json.get("qubits", 0))},
            {i: (i + 3) % self.num_physical for i in range(qade_json.get("qubits", 0))},
            {i: (self.num_physical - 1 - i) % self.num_physical for i in range(qade_json.get("qubits", 0))}
        ]
        
        best_circuit = None
        best_swaps = 999999
        best_layout = None
        
        for lay in layouts:
            p_to_v_lay = {p: v for v, p in lay.items()}
            used_phys = set(p_to_v_lay.keys())
            used_virt = set(p_to_v_lay.values())
            all_phys = set(range(self.num_physical))
            all_virt = set(range(max(qade_json.get("qubits", 0), self.num_physical)))
            rem_phys = sorted(list(all_phys - used_phys))
            rem_virt = sorted(list(all_virt - used_virt))
            for p, v in zip(rem_phys, rem_virt):
                lay[v] = p
                p_to_v_lay[p] = v
                
            routed, final_layout = self._route_sabre(qade_json, lay, p_to_v_lay)
            swaps = sum(1 for g in routed["gates"] if g["type"] == "SWAP")
            
            if swaps < best_swaps:
                best_swaps = swaps
                best_circuit = routed
                best_layout = final_layout
                
        return best_circuit or qade_json, best_layout or v_to_p

    def _route_hybrid(self, qade_json: Dict[str, Any], v_to_p: Dict[int, int], p_to_v: Dict[int, int]) -> Tuple[Dict[str, Any], Dict[int, int]]:
        """Hybrid Router: uses A* pathfinding but fallback-inserts SWAPs adjacent to target lines."""
        # Combines features of A* path routing with local BFS fallback routing
        return self._route_astar(qade_json, v_to_p, p_to_v)
