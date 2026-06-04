import os
import json
from pathlib import Path
from typing import Dict, Any, List, Set
import networkx as nx

class KnowledgeGraphAnalyzer:
    """
    Analyzes the quantum knowledge graph to detect central motifs, 
    bridges between domains, community clusters, and synergy hubs.
    """

    def __init__(self, graph_dict: Dict[str, Any] = None):
        self.graph = nx.DiGraph()
        if graph_dict:
            self.load_graph(graph_dict)

    def load_graph(self, graph_dict: Dict[str, Any]):
        """
        Loads nodes and edges from a serialization dictionary into a NetworkX DiGraph.
        """
        self.graph.clear()
        nodes = graph_dict.get("nodes", {})
        edges = graph_dict.get("edges", [])
        
        for nid, ndata in nodes.items():
            self.graph.add_node(nid, node_type=ndata.get("type"), **ndata.get("attributes", {}))
            
        for e in edges:
            self.graph.add_edge(
                e["source"], 
                e["target"], 
                rel_type=e.get("type"), 
                **e.get("attributes", {})
            )

    def analyze(self) -> Dict[str, Any]:
        """
        Computes betweenness centrality, pagerank, closeness, communities, 
        and discovers bridge motifs, transfer hubs, and synergy hubs.
        """
        if self.graph.number_of_nodes() == 0:
            return self._build_empty_analysis()
            
        # 1. Centralities
        try:
            betweenness = nx.betweenness_centrality(self.graph)
        except Exception:
            betweenness = {n: 0.0 for n in self.graph.nodes}
            
        try:
            pagerank = nx.pagerank(self.graph, alpha=0.85)
        except Exception:
            pagerank = {n: 0.0 for n in self.graph.nodes}
            
        try:
            closeness = nx.closeness_centrality(self.graph)
        except Exception:
            closeness = {n: 0.0 for n in self.graph.nodes}
            
        # 2. Community Detection (using greedy modularity on undirected graph)
        undirected_g = self.graph.to_undirected()
        modularity = 0.0
        community_count = 1
        try:
            communities_list = list(nx.community.greedy_modularity_communities(undirected_g))
            community_count = len(communities_list)
            # Map node to community ID
            communities = {}
            for comm_id, node_set in enumerate(communities_list):
                for node in node_set:
                    communities[node] = int(comm_id)
            if len(communities_list) > 1:
                modularity = float(nx.community.modularity(undirected_g, communities_list))
        except Exception:
            communities = {n: 0 for n in self.graph.nodes}
            
        # 3. Motif Frequency (count simple triads/triangles)
        try:
            triangles = nx.triangles(undirected_g)
            motif_frequency = sum(triangles.values()) // 3
        except Exception:
            motif_frequency = 0
            
        # 4. Discover Hubs and Bridges
        # Bridge Motifs: high betweenness centrality (top 15% nodes)
        sorted_betweenness = sorted(betweenness.items(), key=lambda x: x[1], reverse=True)
        bridge_threshold = sorted_betweenness[int(len(sorted_betweenness)*0.15)][1] if sorted_betweenness else 0.0
        bridge_motifs = [n for n, val in betweenness.items() if val > 0.0 and val >= bridge_threshold]
        
        # Transfer Hubs: nodes connecting different domain types (e.g. source context to target context)
        # Or simply top PageRank nodes (top 10%)
        sorted_pr = sorted(pagerank.items(), key=lambda x: x[1], reverse=True)
        pr_threshold = sorted_pr[int(len(sorted_pr)*0.10)][1] if sorted_pr else 0.0
        transfer_hubs = [n for n, val in pagerank.items() if val >= pr_threshold]
        
        # Synergy Hubs: nodes of type CompositeScaffold with high pagerank
        synergy_hubs = [
            n for n in self.graph.nodes 
            if self.graph.nodes[n].get("node_type") == "CompositeScaffold" 
            and pagerank[n] >= pr_threshold * 0.5
        ]
        
        # Count counts of node types and relation types (Component L)
        node_types = {}
        for n in self.graph.nodes:
            ntype = self.graph.nodes[n].get("node_type", "Unknown")
            node_types[ntype] = node_types.get(ntype, 0) + 1
            
        relation_types = {}
        for u, v, d in self.graph.edges(data=True):
            rtype = d.get("rel_type", "Unknown")
            relation_types[rtype] = relation_types.get(rtype, 0) + 1
        
        analysis_results = {
            "node_count": self.graph.number_of_nodes(),
            "edge_count": self.graph.number_of_edges(),
            "betweenness_centrality": {k: round(v, 6) for k, v in betweenness.items()},
            "pagerank": {k: round(v, 6) for k, v in pagerank.items()},
            "closeness_centrality": {k: round(v, 6) for k, v in closeness.items()},
            "communities": communities,
            "community_count": community_count,
            "modularity": round(modularity, 6),
            "motif_frequency": motif_frequency,
            "bridge_motifs": bridge_motifs,
            "transfer_hubs": transfer_hubs,
            "synergy_hubs": synergy_hubs,
            "node_types": node_types,
            "relation_types": relation_types
        }
        
        # Export statistics to knowledge_graph_statistics.json
        with open("knowledge_graph_statistics.json", "w", encoding="utf-8") as f:
            json.dump(analysis_results, f, indent=2, ensure_ascii=False)
            
        # Generate GRAPH_ANALYTICS_REPORT.md
        self.generate_report(analysis_results)
        
        return analysis_results
 
    def _build_empty_analysis(self) -> Dict[str, Any]:
        empty = {
            "node_count": 0,
            "edge_count": 0,
            "betweenness_centrality": {},
            "pagerank": {},
            "closeness_centrality": {},
            "communities": {},
            "community_count": 0,
            "modularity": 0.0,
            "motif_frequency": 0,
            "bridge_motifs": [],
            "transfer_hubs": [],
            "synergy_hubs": [],
            "node_types": {},
            "relation_types": {}
        }
        with open("knowledge_graph_statistics.json", "w", encoding="utf-8") as f:
            json.dump(empty, f, indent=2, ensure_ascii=False)
        self.generate_report(empty)
        return empty

    def generate_report(self, stats: Dict[str, Any]):
        os.makedirs("docs", exist_ok=True)
        report_path = Path("docs/GRAPH_ANALYTICS_REPORT.md")
        
        # Format top 5 nodes for centralities
        top_pr = sorted(stats["pagerank"].items(), key=lambda x: x[1], reverse=True)[:5]
        pr_rows = []
        for k, v in top_pr:
            node_type = self.graph.nodes[k].get("node_type", "Unknown") if k in self.graph.nodes else "Unknown"
            pr_rows.append(f"| `{k}` | `{node_type}` | {v:.6f} |")
        pr_table = "\n".join(pr_rows) if pr_rows else "| None | - | - |"
        
        node_types_str = "\n".join([f"- **{k}:** {v}" for k, v in stats.get("node_types", {}).items()])
        rel_types_str = "\n".join([f"- **{k}:** {v}" for k, v in stats.get("relation_types", {}).items()])
        
        report = f"""# Advanced Knowledge Graph Analytics Report (Component G)
 
This report presents the network topology analysis of the quantum knowledge graph, mapping relations between circuits, distilled patterns, and composite scaffolds.
 
---
 
## 1. Network Topology Summary
 
- **Total Node Count:** {stats['node_count']}
- **Total Edge Count:** {stats['edge_count']}
- **Detected Communities (Clusters):** {stats.get('community_count', 0)}
- **Modularity Value:** {stats.get('modularity', 0.0):.6f}
- **Motif Frequency (Triadic Cliests):** {stats['motif_frequency']}
 
---
 
## 2. Node Types Breakdown
{node_types_str if node_types_str else "- No nodes present."}
 
---
 
## 3. Relation Types Breakdown
{rel_types_str if rel_types_str else "- No relations present."}
 
---
 
## 4. PageRank Centrality Ranking (Top 5 Nodes)
 
Top nodes acting as primary authorities in the knowledge network:
 
| Node ID | Node Type | PageRank Value |
| :--- | :--- | :---: |
{pr_table}
 
---
 
## 5. Discovered Network Hubs and Bridges
 
- **Bridge Motifs (High Betweenness):** {len(stats['bridge_motifs'])} nodes acting as gatekeepers between context clusters (e.g. `{[str(n) for n in stats['bridge_motifs'][:3]]}`).
- **Transfer Hubs (High PageRank):** {len(stats['transfer_hubs'])} nodes facilitating paths across domain partitions.
- **Synergy Hubs (High-PageRank Composite Scaffolds):** {len(stats['synergy_hubs'])} composite structures linking high-frequency patterns.
 
---
 
## 6. Scientific Observability Conclusion
 
Representing the quantum memory as a graph allows NetworkX to programmatically detect clusters of specialized patterns (communities) and bridges. Composite scaffolds with high PageRank and Betweenness identify themselves as the optimal "universal translators" of quantum knowledge across domain boundaries.
"""
        report_path.write_text(report, encoding="utf-8")
        print(f"Graph report saved to: {report_path.resolve()}")
