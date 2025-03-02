from typing import Dict, List
from ..knowledge.pubtator import PubTatorClient
from ..knowledge.graph import KnowledgeGraph
from ..reasoning.llm_manager import LLMManager
from ..reasoning.hypothesis import HypothesisGenerator
import networkx as nx

class ScientificWorkflow:
    def __init__(self):
        self.pubtator = PubTatorClient()
        self.knowledge_graph = KnowledgeGraph()
        self.llm_manager = LLMManager()
        self.hypothesis_generator = HypothesisGenerator()

    def connect_concepts(self, query: str) -> nx.Graph:
        """
        Create a knowledge graph connecting scientific concepts
        """
        # Identify entities in the query
        entities = self.pubtator.identify_entities(query)

        if entities.empty:
            return nx.Graph()  # Return empty graph if no entities found

        # Create graph nodes for each entity with metadata
        for _, entity in entities.iterrows():
            self.knowledge_graph.add_concept(
                entity["text"],
                {
                    "type": entity["type"],
                    "id": entity["identifier"],
                    "description": entity["description"]
                }
            )

        # Define core relationships
        relationships = [
            ("early life", "development", "temporal context for"),
            ("early life", "antibiotic", "timing of"),
            ("antibiotic", "treatment", "type of"),
            ("treatment", "immune system", "influences"),
            ("immune system", "development", "undergoes"),
            ("molecular mechanisms", "immune system", "governs"),
            ("molecular mechanisms", "treatment", "mediates effects of")
        ]

        # Add relationships to graph
        for source, target, relation in relationships:
            if source in entities["text"].values and target in entities["text"].values:
                self.knowledge_graph.add_relationship(source, target, relation)

        # Add LLM-generated mechanistic relationships
        if len(self.knowledge_graph.graph.edges()) > 0:
            entity_list = entities["text"].tolist()
            for i in range(len(entity_list)):
                for j in range(i+1, len(entity_list)):
                    if (entity_list[i], entity_list[j]) not in relationships:
                        relationship_prompt = f"""
                        Analyze the mechanistic relationship between these concepts in early life antibiotic treatment:
                        1. {entity_list[i]} ({entities.iloc[i]['type']})
                        2. {entity_list[j]} ({entities.iloc[j]['type']})

                        Provide a brief, specific biological mechanism connecting them.
                        """
                        relationship = self.llm_manager.generate_response(relationship_prompt)

                        if relationship and len(relationship.strip()) > 0:
                            self.knowledge_graph.add_relationship(
                                entity_list[i],
                                entity_list[j],
                                relationship.strip()
                            )

        return self.knowledge_graph.graph

    def analyze_research_path(self, start_concept: str, end_concept: str) -> Dict:
        """
        Analyze the research path between two concepts
        """
        path = self.knowledge_graph.find_path(start_concept, end_concept)

        if not path:
            connection_prompt = f"""
            Suggest a molecular mechanism connecting these concepts:
            Start: {start_concept}
            End: {end_concept}

            Focus on:
            1. Cellular pathways
            2. Molecular mediators
            3. Temporal sequence
            4. Causal relationships
            """
            connection = self.llm_manager.generate_response(connection_prompt)

            return {
                "direct_path": False,
                "suggested_connection": connection
            }

        return {
            "direct_path": True,
            "path": path
        }