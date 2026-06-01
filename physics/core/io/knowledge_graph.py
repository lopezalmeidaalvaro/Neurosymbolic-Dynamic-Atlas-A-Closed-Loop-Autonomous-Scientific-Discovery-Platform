#!/usr/bin/env python3
"""
Phase 1: Persistent Causal Knowledge Graph
Author: Antigravity AI & Alvaro Lopez Almeida
"""

import os
import json
import time
import networkx as nx
from networkx.readwrite import json_graph

class ScientificKnowledgeGraph:
    """
    Causal database storing scientific discoveries, hypotheses, 
    experiments, and results as a directed graph.
    """
    def __init__(self, persistence_path="physics/core/io/knowledge_graph.json"):
        self.persistence_path = persistence_path
        self.graph = nx.DiGraph()
        
        # Load from disk if it exists
        self.load_from_json()

    def add_node(self, node_id, node_type, metadata=None):
        """
        Adds a node to the knowledge graph.
        node_type: Hypothesis, Experiment, Metric, Equation, Failure, Success
        """
        if metadata is None:
            metadata = {}
            
        defaults = {
            "type": node_type,
            "timestamp": time.time(),
            "author": "System",
            "confidence": 1.0,
            "results_files": []
        }
        # Merge defaults with custom metadata
        defaults.update(metadata)
        
        self.graph.add_node(node_id, **defaults)
        self.save_to_disk()
        print(f"[+] KnowledgeGraph: Nodo añadido -> {node_id} ({node_type})")

    def add_edge(self, source, target, relation_type, metadata=None):
        """
        Adds a directed edge representing causal relations.
        relation_type: e.g., 'proposes', 'tests', 'yields', 'validates', 'contradicts'
        """
        if metadata is None:
            metadata = {}
            
        defaults = {
            "relation": relation_type,
            "timestamp": time.time()
        }
        defaults.update(metadata)
        
        self.graph.add_edge(source, target, **defaults)
        self.save_to_disk()
        print(f"[+] KnowledgeGraph: Enlace añadido -> [{source}] --({relation_type})--> [{target}]")

    def query_similar(self, node_id, threshold=0.5):
        """
        Queries nodes with similar metadata/features to the given node.
        Computes metadata overlap (keys and values matching).
        """
        if node_id not in self.graph:
            return []
            
        target_attrs = self.graph.nodes[node_id]
        similar_nodes = []
        
        for n, attrs in self.graph.nodes(data=True):
            if n == node_id:
                continue
            # Compare attribute similarity (intersection of shared values / union of keys)
            shared_keys = set(target_attrs.keys()).intersection(set(attrs.keys()))
            if not shared_keys:
                continue
                
            matches = sum(1 for k in shared_keys if target_attrs[k] == attrs[k])
            score = matches / len(shared_keys)
            
            if score >= threshold:
                similar_nodes.append((n, score))
                
        return sorted(similar_nodes, key=lambda x: x[1], reverse=True)

    def export_to_json(self, file_path=None):
        """
        Serializes the NetworkX graph to a standard node-link JSON structure.
        """
        if file_path is None:
            file_path = self.persistence_path
            
        # Create parent directories if they don't exist
        os.makedirs(os.path.dirname(file_path), exist_ok=True)
        
        data = json_graph.node_link_data(self.graph)
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump(data, f, indent=4)
        return file_path

    def load_from_json(self, file_path=None):
        """
        Loads the NetworkX graph from a node-link JSON file.
        """
        if file_path is None:
            file_path = self.persistence_path
            
        if os.path.exists(file_path):
            try:
                with open(file_path, "r", encoding="utf-8") as f:
                    data = json.load(f)
                self.graph = json_graph.node_link_graph(data)
                print(f"[+] KnowledgeGraph: Grafo cargado con éxito desde {file_path}")
            except Exception as e:
                print(f"[!] Error al cargar el grafo de conocimiento: {e}. Inicializando grafo vacío.")
                self.graph = nx.DiGraph()
        else:
            self.graph = nx.DiGraph()

    def save_to_disk(self):
        """
        Quick helper to persist current state.
        """
        self.export_to_json()

if __name__ == "__main__":
    # Standard verification run
    kg = ScientificKnowledgeGraph("physics/core/io/test_graph.json")
    kg.add_node("H1", "Hypothesis", {"author": "HypoGen", "confidence": 0.8})
    kg.add_node("E1", "Experiment", {"author": "ExpPlanner", "results_files": ["sim_1.csv"]})
    kg.add_edge("H1", "E1", "tests")
    print(f"Similar nodes to H1: {kg.query_similar('H1', 0.2)}")
