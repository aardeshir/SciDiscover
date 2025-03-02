"""
Main SciAgent implementation following SciAgents architecture
Enhanced with KG-COI graph reasoning
"""
from typing import Dict, List, Optional
from .llm_manager import LLMManager
from .agents import OntologistAgent, ScientistAgent, ExpanderAgent, CriticAgent
from .kg_reasoning import KGReasoningAgent
import json

class SciAgent:
    """
    Orchestrates multi-agent scientific analysis and discovery
    Based on SciAgents (Ghafarollahi & Buehler, 2024)
    """
    def __init__(self):
        self.llm_manager = LLMManager()
        self.ontologist = OntologistAgent(self.llm_manager)
        self.scientist = ScientistAgent(self.llm_manager)
        self.expander = ExpanderAgent(self.llm_manager)
        self.critic = CriticAgent(self.llm_manager)
        self.kg_reasoner = KGReasoningAgent(self.llm_manager)

    def analyze_mechanism(self, query: str, novelty_score: float = 0.5, include_established: bool = True) -> Dict:
        """
        Perform deep scientific analysis using multi-agent approach
        Args:
            query: Scientific query to analyze
            novelty_score: Target novelty level (0: established, 1: novel)
            include_established: Whether to include well-known mechanisms
        """
        try:
            # Step 1: Ontological Analysis
            print("Starting ontological analysis...")
            concepts = self.ontologist.define_concepts(query)
            print("Ontologist response type:", type(concepts))
            print("Ontologist response:", concepts)

            if not concepts or not isinstance(concepts, dict):
                print("Invalid concept response:", concepts)
                return {
                    "error": "Failed to extract concepts",
                    "primary_analysis": {
                        "pathways": [],
                        "genes": [],
                        "mechanisms": "Analysis failed - concept extraction error",
                        "timeline": [],
                        "evidence": [],
                        "implications": []
                    },
                    "confidence_score": 0
                }

            # Extract concept list
            concept_list = []
            for category in ["molecular_components", "cellular_processes", 
                           "regulatory_mechanisms", "developmental_context"]:
                if category in concepts:
                    concept_list.extend(concepts[category])

            if not concept_list:
                print("No concepts found in categories")
                return {
                    "error": "No relevant concepts found",
                    "primary_analysis": {
                        "pathways": [],
                        "genes": [],
                        "mechanisms": "Analysis failed - no concepts identified",
                        "timeline": [],
                        "evidence": [],
                        "implications": []
                    },
                    "confidence_score": 0
                }

            # Step 2: Graph-based Analysis
            print("Performing graph-based analysis...")
            print(f"Analyzing concepts: {concept_list}")

            graph_analysis = self.kg_reasoner.analyze_mechanism_path(
                query, 
                concept_list,
                novelty_score=novelty_score,
                include_established=include_established
            )

            if "error" in graph_analysis:
                print("Error in graph analysis:", graph_analysis["error"])
                return graph_analysis

            # Return the analysis results
            return {
                "primary_analysis": graph_analysis["primary_analysis"],
                "validation": graph_analysis.get("validation", "No validation available"),
                "confidence_score": graph_analysis.get("confidence_score", 0),
                "graph_analysis": graph_analysis.get("graph_analysis", {})
            }

        except Exception as e:
            print(f"Error in analysis: {str(e)}")
            return {
                "error": f"Analysis error: {str(e)}",
                "primary_analysis": {
                    "pathways": [],
                    "genes": [],
                    "mechanisms": "Analysis failed - unexpected error",
                    "timeline": [],
                    "evidence": [],
                    "implications": []
                },
                "confidence_score": 0
            }