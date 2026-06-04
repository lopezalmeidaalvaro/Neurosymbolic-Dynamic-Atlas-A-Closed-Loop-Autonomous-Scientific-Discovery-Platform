from typing import Dict, Any, List

class QuantumKnowledgeGraph:
    """
    Grafo de conocimiento cuántico ligero en memoria.
    Registra relaciones entre circuitos, patrones extraídos, generaciones y puntuaciones.
    """

    def __init__(self):
        # n_id -> { "type": node_type, "attributes": attributes }
        self.nodes: Dict[str, Dict[str, Any]] = {}
        # Lista de diccionarios { "source": s, "target": t, "type": rel_type, "attributes": attr }
        self.edges: List[Dict[str, Any]] = []

    def add_node(self, node_id: str, node_type: str, **attributes) -> None:
        """
        Añade un nodo al grafo.
        """
        self.nodes[node_id] = {
            "type": node_type,
            "attributes": attributes
        }

    def add_edge(self, source_id: str, target_id: str, edge_type: str, **attributes) -> None:
        """
        Añade una arista dirigida entre dos nodos del grafo.
        """
        self.edges.append({
            "source": source_id,
            "target": target_id,
            "type": edge_type,
            "attributes": attributes
        })

    def get_nodes_by_type(self, node_type: str) -> Dict[str, Dict[str, Any]]:
        """
        Retorna todos los nodos de un tipo determinado.
        """
        return {nid: ndata for nid, ndata in self.nodes.items() if ndata["type"] == node_type}

    def get_edges_by_type(self, edge_type: str) -> List[Dict[str, Any]]:
        """
        Retorna todas las aristas de un tipo determinado.
        """
        return [edge for edge in self.edges if edge["type"] == edge_type]

    def clear(self) -> None:
        """
        Limpia el grafo por completo.
        """
        self.nodes.clear()
        self.edges.clear()

    def to_dict(self) -> Dict[str, Any]:
        """
        Exporta el grafo completo a un diccionario serializable JSON.
        """
        return {
            "nodes": self.nodes,
            "edges": self.edges
        }
