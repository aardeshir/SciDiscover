import networkx as nx
from typing import List, Tuple
import json
import os
from scidiscover.config import GRAPH_CACHE_DIR

class KnowledgeGraph:
    def __init__(self):
        self.graph = nx.Graph()
        os.makedirs(GRAPH_CACHE_DIR, exist_ok=True)

    def add_concept(self, concept: str, properties: dict = None):
        """Add a concept node to the knowledge graph"""
        self.graph.add_node(concept, **properties if properties else {})

    def add_relationship(self, concept1: str, concept2: str, relationship_type: str):
        """Add a relationship between two concepts"""
        self.graph.add_edge(concept1, concept2, type=relationship_type)

    def find_path(self, start_concept: str, end_concept: str) -> List[str]:
        """Find the shortest path between two concepts"""
        try:
            path = nx.shortest_path(self.graph, start_concept, end_concept)
            return path
        except nx.NetworkXNoPath:
            return []

    def get_related_concepts(self, concept: str, max_depth: int = 2) -> List[str]:
        """Get related concepts within specified depth"""
        related = set()
        for node in nx.descendants_at_distance(self.graph, concept, max_depth):
            related.add(node)
        return list(related)

    def save_graph(self, filename: str):
        """Save the knowledge graph to file"""
        path = os.path.join(GRAPH_CACHE_DIR, filename)
        nx.write_gexf(self.graph, path)

    def load_graph(self, filename: str):
        """Load a knowledge graph from file"""
        path = os.path.join(GRAPH_CACHE_DIR, filename)
        if os.path.exists(path):
            self.graph = nx.read_gexf(path)