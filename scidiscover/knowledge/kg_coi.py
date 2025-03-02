"""
KG-COI (Knowledge Graph - Concept Oriented Inference) implementation
Based on Buehler et al. 2024 (Machine Learning: Science and Technology)
"""
from typing import List, Dict, Tuple, Optional
import networkx as nx
import json
from ..config import GRAPH_CACHE_DIR
import os

class KGCOIManager:
    def __init__(self):
        """Initialize KG-COI manager"""
        self.graph = nx.Graph()
        self.cache_dir = GRAPH_CACHE_DIR
        os.makedirs(self.cache_dir, exist_ok=True)

    def build_concept_graph(self, concepts: List[str], relationships: List[Dict]) -> nx.Graph:
        """
        Build a concept-oriented knowledge graph
        Args:
            concepts: List of scientific concepts
            relationships: List of relationship dictionaries between concepts
        """
        # Create concept nodes
        for concept in concepts:
            self.graph.add_node(concept, type="concept")

        # Add relationships with metadata
        for rel in relationships:
            source = rel["source"]
            target = rel["target"]
            rel_type = rel["type"]
            evidence = rel.get("evidence", [])
            
            self.graph.add_edge(
                source,
                target,
                type=rel_type,
                evidence=evidence
            )

        return self.graph

    def sample_concept_paths(self, start_concept: str, end_concept: str, num_paths: int = 5) -> List[List[str]]:
        """
        Sample paths between concepts using random walks
        Args:
            start_concept: Starting concept node
            end_concept: Target concept node
            num_paths: Number of paths to sample
        """
        paths = []
        for _ in range(num_paths):
            try:
                path = nx.shortest_path(self.graph, start_concept, end_concept)
                if path not in paths:
                    paths.append(path)
            except nx.NetworkXNoPath:
                continue

        return paths

    def extract_subgraph(self, concepts: List[str], max_hops: int = 2) -> nx.Graph:
        """
        Extract a relevant subgraph around concepts
        Args:
            concepts: List of central concepts
            max_hops: Maximum path length from concepts
        """
        nodes = set(concepts)
        for concept in concepts:
            for node in nx.single_source_shortest_path_length(self.graph, concept, cutoff=max_hops):
                nodes.add(node)
        
        return self.graph.subgraph(nodes).copy()

    def get_concept_relationships(self, concept: str) -> List[Dict]:
        """
        Get all relationships involving a concept
        Args:
            concept: Target concept
        """
        relationships = []
        for neighbor in self.graph.neighbors(concept):
            edge_data = self.graph.get_edge_data(concept, neighbor)
            relationships.append({
                "source": concept,
                "target": neighbor,
                "type": edge_data["type"],
                "evidence": edge_data.get("evidence", [])
            })
        return relationships

    def save_graph(self, filename: str):
        """Save knowledge graph to cache"""
        path = os.path.join(self.cache_dir, filename)
        nx.write_graphml(self.graph, path)

    def load_graph(self, filename: str):
        """Load knowledge graph from cache"""
        path = os.path.join(self.cache_dir, filename)
        if os.path.exists(path):
            self.graph = nx.read_graphml(path)
