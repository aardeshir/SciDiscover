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

        # Create graph nodes for each entity
        for _, entity in entities.iterrows():
            self.knowledge_graph.add_concept(
                entity["text"],
                {
                    "type": entity["type"],
                    "id": entity["identifier"],
                    "source": entity["source_phrase"]
                }
            )

        # Generate relationships using LLM
        entity_list = entities["text"].tolist()
        for i in range(len(entity_list)):
            for j in range(i+1, len(entity_list)):
                relationship_prompt = f"""
                Analyze the relationship between these scientific concepts in the context of early life antibiotic treatment and immune system development:
                1. {entity_list[i]}
                2. {entity_list[j]}

                Provide a brief, specific relationship description focused on mechanistic connections.
                """
                relationship = self.llm_manager.generate_response(relationship_prompt)

                if relationship:  # Only add edge if relationship was found
                    self.knowledge_graph.add_relationship(
                        entity_list[i],
                        entity_list[j],
                        relationship
                    )

        if len(self.knowledge_graph.graph.edges()) == 0:
            # If no relationships found, create basic connections
            if len(entity_list) >= 2:
                self.knowledge_graph.add_relationship(
                    entity_list[0],
                    entity_list[1],
                    "may influence"
                )

        return self.knowledge_graph.graph

    def analyze_research_path(self, start_concept: str, end_concept: str) -> Dict:
        """
        Analyze the research path between two concepts
        """
        # Find path in knowledge graph
        path = self.knowledge_graph.find_path(start_concept, end_concept)

        if not path:
            # Generate potential connection using LLM
            connection_prompt = f"""
            Suggest a research path connecting these concepts:
            Start: {start_concept}
            End: {end_concept}

            Focus on molecular mechanisms and biological pathways.
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