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

    def analyze_mechanism(self, query: str) -> Dict:
        """
        Perform deep scientific analysis using multi-agent approach
        """
        try:
            # Step 1: Ontological Analysis
            print("Starting ontological analysis...")
            concepts = self.ontologist.define_concepts(query)

            if not concepts or not isinstance(concepts, dict):
                return {"error": "Failed to extract concepts"}

            # Step 2: Graph-based Analysis
            print("Performing graph-based analysis...")
            concept_list = []
            for category in ["molecular_components", "cellular_processes", 
                           "regulatory_mechanisms", "developmental_context"]:
                concept_list.extend(concepts.get(category, []))

            graph_analysis = self.kg_reasoner.analyze_mechanism_path(query, concept_list)

            # Step 3: Initial Hypothesis Generation
            print("Generating initial hypothesis...")
            initial_hypothesis = self.scientist.generate_hypothesis({
                **concepts,
                "graph_evidence": graph_analysis["knowledge_graph"]
            })

            if not initial_hypothesis or not isinstance(initial_hypothesis, dict):
                return {
                    "error": "Failed to generate hypothesis",
                    "concepts": concepts
                }

            # Step 4: Hypothesis Expansion
            print("Expanding hypothesis...")
            expanded = self.expander.expand_hypothesis(initial_hypothesis)

            if not expanded or not isinstance(expanded, dict):
                return {
                    "error": "Failed to expand hypothesis",
                    "initial_hypothesis": initial_hypothesis
                }

            # Step 5: Graph-based Validation
            print("Validating with knowledge graph...")
            graph_validation = self.kg_reasoner.validate_hypothesis({
                **initial_hypothesis,
                "concept_paths": graph_analysis["concept_paths"]
            })

            # Step 6: Critical Review
            print("Performing critical review...")
            full_hypothesis = {
                **initial_hypothesis,
                "expanded_analysis": expanded,
                "graph_validation": graph_validation
            }
            review = self.critic.review_hypothesis(full_hypothesis)

            # Combine all analyses into final output
            return {
                "primary_analysis": {
                    "pathways": initial_hypothesis["mechanisms"]["pathways"] + 
                               expanded["expanded_mechanisms"]["additional_pathways"],
                    "genes": initial_hypothesis["mechanisms"]["genes"],
                    "mechanisms": initial_hypothesis["hypothesis"],
                    "timeline": initial_hypothesis["mechanisms"]["timeline"],
                    "evidence": initial_hypothesis["evidence"],
                    "implications": expanded["therapeutic_implications"]
                },
                "graph_analysis": {
                    "concept_paths": graph_analysis["concept_paths"],
                    "mechanistic_insights": graph_analysis["hypothesis"],
                    "validation": graph_validation
                },
                "expanded_analysis": {
                    "pathway_interactions": expanded["expanded_mechanisms"]["pathway_interactions"],
                    "system_effects": expanded["expanded_mechanisms"]["system_effects"],
                    "research_priorities": expanded["research_priorities"]
                },
                "validation": review["evaluation"],
                "confidence_score": review["confidence_score"]
            }

        except Exception as e:
            print(f"Error in analysis: {str(e)}")
            return {
                "error": f"Analysis error: {str(e)}",
                "details": "An error occurred during the multi-agent analysis process"
            }