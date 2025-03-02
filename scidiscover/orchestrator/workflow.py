from typing import Dict, List
from ..knowledge.pubtator import PubTatorClient
from ..knowledge.graph import KnowledgeGraph
from ..reasoning.llm_manager import LLMManager
from ..reasoning.hypothesis import HypothesisGenerator

class ScientificWorkflow:
    def __init__(self):
        self.pubtator = PubTatorClient()
        self.knowledge_graph = KnowledgeGraph()
        self.llm_manager = LLMManager()
        self.hypothesis_generator = HypothesisGenerator()
        
    def connect_concepts(self, query: str) -> KnowledgeGraph:
        """
        Create a knowledge graph connecting scientific concepts
        """
        # Identify entities in the query
        entities = self.pubtator.identify_entities(query)
        
        # Create graph nodes for each entity
        for _, entity in entities.iterrows():
            self.knowledge_graph.add_concept(
                entity["text"],
                {"type": entity["type"], "id": entity["identifier"]}
            )
            
        # Generate relationships using LLM
        for i in range(len(entities)):
            for j in range(i+1, len(entities)):
                relationship_prompt = f"""
                Describe the relationship between these scientific concepts:
                1. {entities.iloc[i]["text"]}
                2. {entities.iloc[j]["text"]}
                """
                relationship = self.llm_manager.generate_response(relationship_prompt)
                
                self.knowledge_graph.add_relationship(
                    entities.iloc[i]["text"],
                    entities.iloc[j]["text"],
                    relationship
                )
                
        return self.knowledge_graph
        
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
