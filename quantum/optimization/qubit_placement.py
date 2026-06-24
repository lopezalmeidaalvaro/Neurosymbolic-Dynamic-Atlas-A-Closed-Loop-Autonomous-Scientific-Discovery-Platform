import random
from typing import Dict, List, Tuple, Any, Set, Optional

from quantum.optimization.hardware_cost_model import (
    DEFAULT_READOUT_ERROR,
    DEFAULT_T1_SEC,
    DEFAULT_T2_SEC,
    get_gate_properties,
    get_qubit_quality,
)

class QubitPlacement:
    """
    Computes initial virtual-to-physical qubit mapping (layout)
    to minimize physical routing overhead on target coupling maps.
    """
    def __init__(
        self,
        num_logical: int,
        coupling_map: Optional[List[Tuple[int, int]]],
        backend: Optional[Any] = None,
    ):
        self.num_logical = num_logical
        self.backend = backend
        if coupling_map is None and backend is not None and getattr(backend, "coupling_map", None) is not None:
            coupling_map = list(backend.coupling_map)
        self.coupling_map = coupling_map or []
        
        # Determine number of physical qubits from coupling map
        if backend is not None and getattr(backend, "num_qubits", None):
            self.num_physical = backend.num_qubits
        elif self.coupling_map:
            self.num_physical = max(max(edge) for edge in self.coupling_map) + 1
        else:
            self.num_physical = num_logical
            
        # Build physical adjacency and distance matrices
        self.adj = {i: set() for i in range(self.num_physical)}
        if self.coupling_map:
            for u, v in self.coupling_map:
                self.adj[u].add(v)
                self.adj[v].add(u)
                
        self.dist_matrix = self._compute_all_pairs_shortest_paths()

    def _compute_all_pairs_shortest_paths(self) -> Dict[int, Dict[int, int]]:
        dist = {i: {j: 9999 for j in range(self.num_physical)} for i in range(self.num_physical)}
        for i in range(self.num_physical):
            dist[i][i] = 0
            for neighbor in self.adj[i]:
                dist[i][neighbor] = 1
                
        # Floyd-Warshall
        for k in range(self.num_physical):
            for i in range(self.num_physical):
                for j in range(self.num_physical):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
        return dist

    def _build_interaction_graph(self, qade_json: Dict[str, Any]) -> Dict[int, Dict[int, float]]:
        """Constructs logical interaction graph with two-qubit gate weights."""
        interactions = {i: {j: 0.0 for j in range(self.num_logical)} for i in range(self.num_logical)}
        for gate in qade_json.get("gates", []):
            q = gate.get("qubits", [])
            if len(q) == 2:
                q0, q1 = q[0], q[1]
                if q0 < self.num_logical and q1 < self.num_logical:
                    interactions[q0][q1] += 1.0
                    interactions[q1][q0] += 1.0
        return interactions

    def place(self, qade_json: Dict[str, Any], method: str = "interaction") -> Dict[int, int]:
        """
        Calculates initial layout mapping.
        Returns: Dict[virtual_qubit: physical_qubit]
        """
        method_key = method.replace("-", "_").lower()

        if not self.coupling_map or self.num_physical <= 1:
            return {i: i for i in range(self.num_logical)}
            
        if method_key == "interaction":
            return self._interaction_placement(qade_json)
        elif method_key in ("distance", "distance_aware"):
            return self._distance_placement(qade_json)
        elif method_key == "look_ahead":
            return self._look_ahead_placement(qade_json)
        elif method_key in ("fidelity", "fidelity_aware", "hardware_aware"):
            return self._fidelity_aware_placement(qade_json)
        else:
            # Fallback to default trivial placement
            return {i: i for i in range(self.num_logical)}

    def _logical_activity(self, qade_json: Dict[str, Any]) -> List[Tuple[int, float]]:
        activity = {i: 0.0 for i in range(self.num_logical)}
        for gate in qade_json.get("gates", []):
            qubits = gate.get("qubits", [])
            weight = 2.0 if len(qubits) == 2 else 1.0
            for q in qubits:
                if q in activity:
                    activity[q] += weight
        ranked = sorted(activity.items(), key=lambda item: item[1], reverse=True)
        return ranked

    def _physical_avg_gate_error(self, physical_qubit: int) -> float:
        if self.backend is None:
            degree = len(self.adj.get(physical_qubit, ()))
            return 1.0 / (degree + 1.0)

        errors = []
        for gate_name in ("sx", "x"):
            errors.append(get_gate_properties(self.backend, gate_name, (physical_qubit,))["error"])
        for neighbor in self.adj.get(physical_qubit, ()):
            two_q_errors = [
                get_gate_properties(self.backend, gate_name, (physical_qubit, neighbor))["error"]
                for gate_name in ("cx", "ecr", "cz")
            ]
            errors.append(min(two_q_errors))
        return sum(errors) / len(errors) if errors else 0.01

    def _fidelity_aware_placement(self, qade_json: Dict[str, Any]) -> Dict[int, int]:
        """Assigns the most active logical qubits to highest-quality physical qubits."""
        self.fallback_activated = False
        qualities = {}
        max_t1 = DEFAULT_T1_SEC
        max_t2 = DEFAULT_T2_SEC
        for p in range(self.num_physical):
            if self.backend is not None:
                quality = get_qubit_quality(self.backend, p)
            else:
                quality = {
                    "t1": DEFAULT_T1_SEC,
                    "t2": DEFAULT_T2_SEC,
                    "readout_error": DEFAULT_READOUT_ERROR,
                }
            quality["avg_gate_error"] = self._physical_avg_gate_error(p)
            quality["degree"] = len(self.adj.get(p, ()))
            qualities[p] = quality
            max_t1 = max(max_t1, quality["t1"])
            max_t2 = max(max_t2, quality["t2"])

        # Calculate active qubit interaction density to dynamically adjust weights.
        # Dense circuits (like QFT) suffer from routing overhead when we avoid readout-noisy qubits.
        active_qs = set()
        num_2q_gates = 0
        for gate in qade_json.get("gates", []):
            if gate.get("type", "").upper() not in ("BARRIER", "MEASURE"):
                q = gate.get("qubits", [])
                active_qs.update(q)
                if len(q) == 2:
                    num_2q_gates += 1
        
        n_act = len(active_qs)
        gate_density = num_2q_gates / n_act if n_act > 0 else 0.0
        
        if gate_density > 3.0:
            w1, w2, w3, w4 = 0.35, 0.35, 0.15, 0.15
        else:
            w1, w2, w3, w4 = 0.225, 0.225, 0.30, 0.25
        physical_scores = []
        for p, quality in qualities.items():
            score = (
                w1 * (quality["t1"] / max_t1)
                + w2 * (quality["t2"] / max_t2)
                - w3 * quality["readout_error"]
                - w4 * quality["avg_gate_error"]
                + 0.01 * quality["degree"]
            )
            physical_scores.append((p, score))
        physical_scores.sort(key=lambda item: item[1], reverse=True)

        qubit_scores = {p: score for p, score in physical_scores}

        # Get active qubits
        active_qs = set()
        for gate in qade_json.get("gates", []):
            if gate.get("type", "").upper() not in ("BARRIER", "MEASURE"):
                active_qs.update(gate.get("qubits", []))
        active_list = sorted(list(active_qs))
        num_active = len(active_list) if active_list else self.num_logical

        # Subgraph path-based search for small linear active circuits (num_active <= 8)
        if num_active <= 8:
            active_to_idx = {q: i for i, q in enumerate(active_list)}
            idx_to_active = {i: q for i, q in enumerate(active_list)}
            
            active_gates = []
            for gate in qade_json.get("gates", []):
                if gate.get("type", "").upper() not in ("BARRIER", "MEASURE"):
                    g_qs = gate.get("qubits", [])
                    if all(q in active_to_idx for q in g_qs):
                        new_gate = gate.copy()
                        new_gate["qubits"] = [active_to_idx[q] for q in g_qs]
                        active_gates.append(new_gate)
                        
            active_qade_json = {
                "qubits": num_active,
                "gates": active_gates
            }
            
            # Helper to find logical chain structure (using num_active)
            def find_logical_chain(n_act: int, inters: Dict[int, Dict[int, float]]) -> Optional[List[int]]:
                neighbors = {i: [] for i in range(n_act)}
                for u in range(n_act):
                    for v, weight in inters[u].items():
                        if weight > 0:
                            neighbors[u].append(v)
                for i in range(n_act):
                    if len(neighbors[i]) > 2:
                        return None
                endpoints = [i for i in range(n_act) if len(neighbors[i]) == 1]
                isolated = [i for i in range(n_act) if len(neighbors[i]) == 0]
                if len(isolated) == n_act:
                    return list(range(n_act))
                if len(endpoints) != 2:
                    if len(endpoints) == 0 and len(isolated) == 0:
                        start = 0
                    else:
                        return None
                else:
                    start = endpoints[0]
                chain = [start]
                visited = {start}
                current = start
                while len(chain) < (n_act - len(isolated)):
                    next_nodes = [n for n in neighbors[current] if n not in visited]
                    if not next_nodes:
                        break
                    next_node = next_nodes[0]
                    chain.append(next_node)
                    visited.add(next_node)
                    current = next_node
                for i in range(n_act):
                    if i not in visited:
                        chain.append(i)
                return chain

            # Build interaction graph for active qubits
            def build_active_interactions(json_data: Dict[str, Any], n_act: int) -> Dict[int, Dict[int, float]]:
                inters = {i: {j: 0.0 for j in range(n_act)} for i in range(n_act)}
                for gate in json_data.get("gates", []):
                    q = gate.get("qubits", [])
                    if len(q) == 2:
                        q0, q1 = q[0], q[1]
                        if q0 < n_act and q1 < n_act:
                            inters[q0][q1] += 1.0
                            inters[q1][q0] += 1.0
                return inters

            active_interactions = build_active_interactions(active_qade_json, num_active)
            logical_chain = find_logical_chain(num_active, active_interactions)
            
            if logical_chain is not None:
                # Helper to find all physical paths of length N in coupling map
                def find_all_physical_paths(adj: Dict[int, set], length: int, max_paths: int = 5000) -> List[List[int]]:
                    paths = []
                    def dfs(node, current_path):
                        if len(paths) >= max_paths:
                            return
                        if len(current_path) == length:
                            paths.append(list(current_path))
                            return
                        for neighbor in adj[node]:
                            if neighbor not in current_path:
                                current_path.append(neighbor)
                                dfs(neighbor, current_path)
                                current_path.pop()
                    for start_node in range(len(adj)):
                        if len(paths) >= max_paths:
                            break
                        dfs(start_node, [start_node])
                    return paths

                # Helper to calculate 2Q edge error
                def get_edge_error(u: int, v: int) -> float:
                    if self.backend is None:
                        return 0.01
                    two_q_errors = []
                    for gate_name in ("cx", "ecr", "cz"):
                        try:
                            err = get_gate_properties(self.backend, gate_name, (u, v))["error"]
                            two_q_errors.append(err)
                        except Exception:
                            pass
                    return min(two_q_errors) if two_q_errors else 0.01

                physical_paths = find_all_physical_paths(self.adj, num_active, max_paths=5000)
                if physical_paths:
                    best_path = None
                    best_path_score = -float("inf")
                    for path in physical_paths:
                        q_score = sum(qubit_scores.get(p, 0.0) for p in path)
                        path_gate_err = sum(get_edge_error(path[i], path[i+1]) for i in range(len(path) - 1))
                        path_score = q_score - path_gate_err
                        if path_score > best_path_score:
                            best_path_score = path_score
                            best_path = path
                    
                    if best_path is not None:
                        # Compute trivial path score for logging
                        trivial_path = list(range(min(num_active, self.num_physical)))
                        trivial_q_score = sum(qubit_scores.get(p, 0.0) for p in trivial_path)
                        trivial_gate_err = sum(get_edge_error(trivial_path[i], trivial_path[i+1]) for i in range(len(trivial_path) - 1))
                        self.last_trivial_path_score = trivial_q_score - trivial_gate_err
                        self.last_selected_path_score = best_path_score
                        
                        # Fallback logic check
                        use_fallback = False
                        fallback_reason = ""
                        
                        if best_path_score < self.last_trivial_path_score:
                            use_fallback = True
                            fallback_reason = f"Selected path score ({best_path_score:.4f}) is lower than trivial path score ({self.last_trivial_path_score:.4f})"
                        
                        # Estimate physical state fidelity for both paths
                        def estimate_path_fidelity(p_path):
                            fid = 1.0
                            for p in p_path:
                                qual = qualities.get(p, {})
                                ro_err = qual.get("readout_error", DEFAULT_READOUT_ERROR)
                                fid *= (1.0 - ro_err)
                            for i in range(len(p_path) - 1):
                                g_err = get_edge_error(p_path[i], p_path[i+1])
                                fid *= (1.0 - g_err)
                            return fid
                            
                        selected_fid = estimate_path_fidelity(best_path)
                        trivial_fid = estimate_path_fidelity(trivial_path)
                        
                        max_allowed_ro = 0.05
                        max_allowed_gate = 0.03
                        
                        has_high_noise = False
                        for p in best_path:
                            qual = qualities.get(p, {})
                            ro_err = qual.get("readout_error", DEFAULT_READOUT_ERROR)
                            gate_err = qual.get("avg_gate_error", 0.01)
                            if ro_err > max_allowed_ro or gate_err > max_allowed_gate:
                                has_high_noise = True
                                
                        if not use_fallback:
                            if selected_fid < trivial_fid:
                                use_fallback = True
                                fallback_reason = f"Selected path estimated fidelity ({selected_fid:.4f}) is lower than trivial path estimated fidelity ({trivial_fid:.4f})"
                            elif has_high_noise and trivial_fid > selected_fid * 0.95:
                                use_fallback = True
                                fallback_reason = "Selected path contains high-noise qubits (readout > 5% or gate > 3%)"
                                
                        if use_fallback:
                            print(f"  [Placement Fallback] Trivial layout [0..N-1] selected. Reason: {fallback_reason}")
                            self.last_selected_path_score = self.last_trivial_path_score
                            self.fallback_activated = True
                            return {logical: logical for logical in range(self.num_logical)}

                        layout = {}
                        placed_physical = set()
                        for i, logical_idx in enumerate(logical_chain):
                            layout[idx_to_active[logical_idx]] = best_path[i]
                            placed_physical.add(best_path[i])
                            
                        # Map remaining idle logical qubits to remaining physical qubits
                        for logical in range(self.num_logical):
                            if logical not in layout:
                                for phys, _ in physical_scores:
                                    if phys not in placed_physical:
                                        layout[logical] = phys
                                        placed_physical.add(phys)
                                        break
                                else:
                                    layout[logical] = logical
                        return layout

        # Fallback to greedy algorithm if num_logical > 8, or not linear, or no physical paths found
        # Fix 2: For dense circuits (like QFT with all-to-all connectivity), the greedy
        # algorithm scatters qubits across the chip causing massive SWAP overhead.
        # Force trivial layout for these cases since trivially-placed qubits on
        # ibm_fez [0,1,2,3,4...] are linearly connected and minimize routing.
        interaction_pairs = set()
        for gate in qade_json.get("gates", []):
            q = gate.get("qubits", [])
            if len(q) == 2:
                pair = (min(q[0], q[1]), max(q[0], q[1]))
                interaction_pairs.add(pair)
        n_pairs = len(interaction_pairs)
        max_pairs = n_act * (n_act - 1) / 2 if n_act > 1 else 1
        pair_density = n_pairs / max_pairs if max_pairs > 0 else 0.0

        if pair_density > 0.5:
            # Dense circuit: trivial layout avoids routing overhead
            print(f"  [Placement Fallback] Dense circuit detected (pair_density={pair_density:.2f}). Using trivial layout.")
            self.fallback_activated = True
            self.last_trivial_path_score = None
            self.last_selected_path_score = None
            return {i: i for i in range(self.num_logical)}

        interactions = self._build_interaction_graph(qade_json)
        layout = {}
        placed_physical = set()

        for logical_qubit, _activity in self._logical_activity(qade_json):
            best_phys = None
            best_cost = float("inf")
            placed_neighbors = [
                (neighbor, weight)
                for neighbor, weight in interactions[logical_qubit].items()
                if weight > 0 and neighbor in layout
            ]

            for phys, quality_score in physical_scores:
                if phys in placed_physical:
                    continue
                if placed_neighbors:
                    distance_cost = sum(
                        weight * self.dist_matrix[phys][layout[neighbor]]
                        for neighbor, weight in placed_neighbors
                    )
                else:
                    distance_cost = 0.0

                cost = distance_cost - 0.25 * quality_score
                if cost < best_cost:
                    best_cost = cost
                    best_phys = phys

            if best_phys is None:
                best_phys = logical_qubit
            layout[logical_qubit] = best_phys
            placed_physical.add(best_phys)

        for logical_qubit in range(self.num_logical):
            if logical_qubit in layout:
                continue
            for phys, _ in physical_scores:
                if phys not in placed_physical:
                    layout[logical_qubit] = phys
                    placed_physical.add(phys)
                    break
            else:
                layout[logical_qubit] = logical_qubit
        return layout

    def _interaction_placement(self, qade_json: Dict[str, Any]) -> Dict[int, int]:
        """Maps logical qubits with high interaction to physical qubits with high connectivity."""
        interactions = self._build_interaction_graph(qade_json)
        
        # Calculate total interaction strength for each logical qubit
        logical_weights = []
        for i in range(self.num_logical):
            logical_weights.append((i, sum(interactions[i].values())))
        # Sort descending
        logical_weights.sort(key=lambda x: x[1], reverse=True)
        
        # Calculate physical qubit connectivity (degree)
        physical_degrees = []
        for i in range(self.num_physical):
            physical_degrees.append((i, len(self.adj[i])))
        # Sort descending
        physical_degrees.sort(key=lambda x: x[1], reverse=True)
        
        # Assign mapping
        layout = {}
        for rank, (l_qubit, _) in enumerate(logical_weights):
            if rank < len(physical_degrees):
                layout[l_qubit] = physical_degrees[rank][0]
            else:
                # Handle cases where physical qubits are fewer (should not happen on actual backends)
                layout[l_qubit] = l_qubit
        return layout

    def _distance_placement(self, qade_json: Dict[str, Any]) -> Dict[int, int]:
        """Greedy placement minimizing physical distance of interacting qubits."""
        interactions = self._build_interaction_graph(qade_json)
        
        # Get logical qubits sorted by total interaction strength
        logical_weights = []
        for i in range(self.num_logical):
            logical_weights.append((i, sum(interactions[i].values())))
        logical_weights.sort(key=lambda x: x[1], reverse=True)
        
        # Sort physical qubits by degree to find the root/center
        physical_candidates = []
        for i in range(self.num_physical):
            physical_candidates.append((i, len(self.adj[i])))
        physical_candidates.sort(key=lambda x: x[1], reverse=True)
        
        layout = {}
        placed_physical = set()
        
        # Place the first (most active) logical qubit in the most central physical qubit
        root_logical = logical_weights[0][0]
        root_physical = physical_candidates[0][0]
        layout[root_logical] = root_physical
        placed_physical.add(root_physical)
        
        # Place remaining qubits greedily
        for l_qubit, _ in logical_weights[1:]:
            # Find all placed logical neighbors and their physical mappings
            placed_neighbors = []
            for neighbor, weight in enumerate(interactions[l_qubit].values()):
                if weight > 0 and neighbor in layout:
                    placed_neighbors.append((layout[neighbor], weight))
            
            # Find the unplaced physical qubit that minimizes the weighted distance to placed neighbors
            best_phys = -1
            best_cost = 999999
            
            for p in range(self.num_physical):
                if p in placed_physical:
                    continue
                cost = 0
                for p_neigh, weight in placed_neighbors:
                    cost += weight * self.dist_matrix[p][p_neigh]
                
                # Add degree penalty to prefer high-degree qubits in ties
                degree_penalty = 1.0 / (len(self.adj[p]) + 1)
                cost += degree_penalty
                
                if cost < best_cost:
                    best_cost = cost
                    best_phys = p
            
            if best_phys == -1:
                # Fallback to any unplaced qubit
                unplaced = list(set(range(self.num_physical)) - placed_physical)
                best_phys = unplaced[0] if unplaced else l_qubit
                
            layout[l_qubit] = best_phys
            placed_physical.add(best_phys)
            
        return layout

    def _look_ahead_placement(self, qade_json: Dict[str, Any]) -> Dict[int, int]:
        """Generates multiple randomized placements and selects the one with lowest early routing cost."""
        best_layout = None
        best_cost = 999999
        
        # Generate 15 candidate layouts
        random_gen = random.Random(42)
        candidates = []
        
        # 1. Add trivial layout
        candidates.append({i: i % self.num_physical for i in range(self.num_logical)})
        # 2. Add interaction graph layout
        candidates.append(self._interaction_placement(qade_json))
        # 3. Add distance layout
        candidates.append(self._distance_placement(qade_json))
        
        # 4. Add randomized distance layout variants
        for _ in range(12):
            layout = {}
            placed = set()
            # Randomize root physical assignment from top 5 central physical qubits
            root_logical = 0
            physical_candidates = sorted(range(self.num_physical), key=lambda x: len(self.adj[x]), reverse=True)
            root_physical = random_gen.choice(physical_candidates[:5])
            layout[root_logical] = root_physical
            placed.add(root_physical)
            
            # Place others greedily but with slight noise in distance cost
            logical_qubits = list(range(self.num_logical))
            random_gen.shuffle(logical_qubits)
            for l in logical_qubits:
                if l in layout:
                    continue
                best_p = -1
                best_c = 99999
                for p in range(self.num_physical):
                    if p in placed:
                        continue
                    cost = 0
                    for placed_l, p_target in layout.items():
                        cost += self.dist_matrix[p][p_target] * (1.0 + random_gen.uniform(-0.1, 0.1))
                    if cost < best_c:
                        best_c = cost
                        best_p = p
                if best_p == -1:
                    unplaced = list(set(range(self.num_physical)) - placed)
                    best_p = unplaced[0] if unplaced else l
                layout[l] = best_p
                placed.add(best_p)
            candidates.append(layout)
            
        # Evaluate lookahead cost of first 20 gates
        early_gates = qade_json.get("gates", [])[:20]
        for layout in candidates:
            cost = 0
            for gate in early_gates:
                q = gate.get("qubits", [])
                if len(q) == 2:
                    p0 = layout.get(q[0], q[0])
                    p1 = layout.get(q[1], q[1])
                    cost += self.dist_matrix[p0][p1]
            if cost < best_cost:
                best_cost = cost
                best_layout = layout
                
        return best_layout or candidates[0]
