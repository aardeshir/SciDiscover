"""
KG-COI (Knowledge Graph - Concept Oriented Inference) implementation
Based on Buehler et al. 2024 (Machine Learning: Science and Technology)
"""
from typing import List, Dict, Tuple, Optional
import networkx as nx
import json
from ..config import GRAPH_CACHE_DIR
import os
import random
import numpy as np

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

    def build_evidence_weighted_graph(self, concepts: List[Dict], relationships: List[Dict]) -> nx.Graph:
        """
        Build a knowledge graph with evidence-weighted edges
        Args:
            concepts: List of concept dictionaries with metadata
            relationships: List of relationship dictionaries with evidence
        """
        # Clear existing graph
        self.graph = nx.Graph()

        # Add concept nodes with metadata
        for concept in concepts:
            self.graph.add_node(
                concept["text"], 
                type=concept.get("type", "concept"),
                confidence=concept.get("confidence", 0.5),
                source=concept.get("source", "unknown")
            )

        # Add relationship edges with evidence weighting
        for rel in relationships:
            # Calculate evidence strength
            evidence_count = len(rel.get("evidence", []))
            pub_years = [e.get("year", 2020) for e in rel.get("evidence", [])]
            recency_factor = sum([(y - 2000)/20 for y in pub_years]) / max(1, len(pub_years))

            # Combine evidence factors into edge weight
            weight = 0.5  # Base weight
            if evidence_count > 0:
                # More evidence = higher weight
                weight += min(0.4, evidence_count * 0.1)

            # Recency bonus/penalty
            weight += recency_factor * 0.1

            # Add the edge with calculated weight
            self.graph.add_edge(
                rel["source"],
                rel["target"],
                type=rel.get("type", "relates_to"),
                weight=weight,
                evidence_count=evidence_count,
                evidence=rel.get("evidence", [])
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

    def enhanced_concept_paths(self, start_concept: str, end_concept: str, num_paths: int = 5, 
                             max_path_length: int = 10, novelty_weight: float = 3.0) -> List[List[str]]:
        """
        Enhanced path sampling using weighted random walks and node centrality metrics
        Args:
            start_concept: Starting concept node
            end_concept: Target concept node
            num_paths: Number of paths to return
            max_path_length: Maximum length of a path
            novelty_weight: Weighting factor for encouraging exploration of novel paths
        Returns:
            List of diverse concept paths between start and end concepts
        """
        # Calculate node centrality to weight important concepts
        try:
            centrality = nx.betweenness_centrality(self.graph)
        except:
            # Fallback if centrality calculation fails
            centrality = {node: 1.0 for node in self.graph.nodes()}

        # Use centrality for weighted random walks
        paths = []
        attempts = num_paths * 4  # Sample more paths than needed to ensure diversity

        for _ in range(attempts):
            current = start_concept
            path = [current]
            visited = {current}

            while current != end_concept and len(path) < max_path_length:
                neighbors = list(self.graph.neighbors(current))
                if not neighbors:
                    break

                # Weight by centrality, edge weight and novelty (not yet visited)
                weights = []
                for neighbor in neighbors:
                    # Base weight from centrality
                    w = centrality.get(neighbor, 0.1)

                    # Include edge weight if available
                    edge_data = self.graph.get_edge_data(current, neighbor)
                    if edge_data and 'weight' in edge_data:
                        w *= edge_data['weight']

                    # Boost for nodes not yet visited in this path
                    if neighbor not in visited:
                        w *= novelty_weight

                    # Boost for nodes closer to target (if we can compute shortest path)
                    try:
                        target_distance = nx.shortest_path_length(self.graph, neighbor, end_concept)
                        # Lower distance = higher weight
                        w *= (1.0 + 1.0/max(1, target_distance))
                    except:
                        # If no path exists, no boost
                        pass

                    weights.append(max(0.01, w))  # Ensure positive weight

                # Probabilistic next step
                if sum(weights) > 0:
                    next_node = random.choices(neighbors, weights=weights)[0]
                else:
                    next_node = random.choice(neighbors)

                path.append(next_node)
                visited.add(next_node)
                current = next_node

            if current == end_concept:
                paths.append(path)

        # Select most diverse paths
        return self._diversify_paths(paths, num_paths)

    def _diversify_paths(self, paths: List[List[str]], num_paths: int) -> List[List[str]]:
        """
        Select a diverse subset of paths to maximize coverage of concept space
        Args:
            paths: List of candidate paths
            num_paths: Number of paths to select
        Returns:
            List of diverse paths
        """
        if not paths:
            return []

        if len(paths) <= num_paths:
            return paths

        # Start with the shortest path
        paths.sort(key=len)
        selected = [paths[0]]
        remaining = paths[1:]

        # Iteratively add the most diverse path
        while len(selected) < num_paths and remaining:
            max_diversity = -1
            most_diverse_idx = 0

            for i, path in enumerate(remaining):
                # Calculate diversity as average Jaccard distance to existing paths
                path_set = set(path)
                diversity = 0

                for sel_path in selected:
                    sel_path_set = set(sel_path)
                    # Jaccard distance: 1 - intersection/union
                    intersection = len(path_set.intersection(sel_path_set))
                    union = len(path_set.union(sel_path_set))
                    if union > 0:
                        diversity += 1 - (intersection / union)

                avg_diversity = diversity / len(selected)
                if avg_diversity > max_diversity:
                    max_diversity = avg_diversity
                    most_diverse_idx = i

            # Add the most diverse path
            selected.append(remaining[most_diverse_idx])
            remaining.pop(most_diverse_idx)

        return selected

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

    def extract_community_subgraph(self, concepts: List[str], community_detection: str = "louvain") -> nx.Graph:
        """
        Extract a subgraph containing the communities of the input concepts
        Args:
            concepts: List of central concepts
            community_detection: Algorithm to use for community detection
        Returns:
            Subgraph containing communities of interest
        """
        # First extract a larger neighborhood around the concepts
        extended_neighborhood = self.extract_subgraph(concepts, max_hops=3)

        # Detect communities
        if community_detection == "louvain":
            try:
                import community as community_louvain
                communities = community_louvain.best_partition(extended_neighborhood)
            except ImportError:
                # Fallback to connected components if community detection package not available
                communities = {}
                for i, component in enumerate(nx.connected_components(extended_neighborhood)):
                    for node in component:
                        communities[node] = i
        else:
            # Simple connected components as fallback
            communities = {}
            for i, component in enumerate(nx.connected_components(extended_neighborhood)):
                for node in component:
                    communities[node] = i

        # Find which communities our concepts belong to
        target_communities = set()
        for concept in concepts:
            if concept in communities:
                target_communities.add(communities[concept])

        # Extract nodes in the target communities
        community_nodes = set()
        for node, comm_id in communities.items():
            if comm_id in target_communities:
                community_nodes.add(node)

        # Return the subgraph of community nodes
        return extended_neighborhood.subgraph(community_nodes).copy()

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

    def get_concept_importance(self, method: str = "pagerank") -> Dict[str, float]:
        """
        Calculate importance scores for all concepts in the graph
        Args:
            method: Method to use for importance calculation
        Returns:
            Dictionary mapping concept names to importance scores
        """
        if method == "pagerank":
            return nx.pagerank(self.graph)
        elif method == "betweenness":
            return nx.betweenness_centrality(self.graph)
        elif method == "eigenvector":
            return nx.eigenvector_centrality_numpy(self.graph)
        elif method == "degree":
            return {node: score/len(self.graph) for node, score in dict(self.graph.degree()).items()}
        else:
            # Default to degree
            return {node: score/len(self.graph) for node, score in dict(self.graph.degree()).items()}

    def save_graph(self, filename: str):
        """Save knowledge graph to cache"""
        path = os.path.join(self.cache_dir, filename)
        nx.write_graphml(self.graph, path)

    def load_graph(self, filename: str):
        """Load knowledge graph from cache"""
        path = os.path.join(self.cache_dir, filename)
        if os.path.exists(path):
            self.graph = nx.read_graphml(path)