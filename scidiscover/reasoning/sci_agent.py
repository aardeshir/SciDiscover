"""
Main SciAgent implementation following SciAgents architecture
Enhanced with KG-COI graph reasoning
"""
from typing import Dict, List, Optional, Callable
from .llm_manager import LLMManager
from .agents import OntologistAgent, ScientistAgent, ExpanderAgent, CriticAgent
from .kg_reasoning import KGReasoningAgent
from .debate_orchestrator import DebateOrchestrator
import json

class SciAgent:
    """
    Orchestrates multi-agent scientific analysis and discovery
    Based on SciAgents (Ghafarollahi & Buehler, 2024)
    """
    def __init__(self, high_demand_mode=True):
        self.llm_manager = LLMManager(high_demand_mode=high_demand_mode)
        self.ontologist = OntologistAgent(self.llm_manager)
        self.scientist = ScientistAgent(self.llm_manager)
        self.expander = ExpanderAgent(self.llm_manager)
        self.critic = CriticAgent(self.llm_manager)
        self.kg_reasoner = KGReasoningAgent(self.llm_manager)
        self.debate_orchestrator = DebateOrchestrator(self.llm_manager)
        self.high_demand_mode = high_demand_mode
        self.debate_callback = None
        self.thinking_mode = "high" if high_demand_mode else "low"

    def set_thinking_mode(self, mode="high"):
        """
        Set the thinking mode for Claude's extended thinking capabilities
        Args:
            mode: "high" for 64K thinking tokens, "low" for 32K thinking tokens, "none" for no extended thinking
        """
        self.thinking_mode = mode.lower()
        self.high_demand_mode = (mode.lower() == "high")
        self.llm_manager.set_thinking_mode(mode)
        print(f"SciAgent thinking mode set to: {mode.title()}")

    def set_debate_callback(self, callback: Callable):
        """
        Set a callback function that will be called whenever there's a new debate update
        Args:
            callback: A function that takes a debate entry dictionary as input
        """
        self.debate_callback = callback
        # Pass the callback to the debate orchestrator
        self.debate_orchestrator.set_update_callback(self.debate_callback)

    def analyze_mechanism(self, query: str, novelty_score: float = 0.5, include_established: bool = True) -> Dict:
        """
        Perform deep scientific analysis using multi-agent approach
        Args:
            query: Scientific query to analyze
            novelty_score: Target novelty level (0: established, 1: novel)
            include_established: Whether to include well-known mechanisms
        """
        try:
            print(f"Starting analysis of query: {query}")
            print(f"Novelty score: {novelty_score}, Include established: {include_established}")
            print(f"Using thinking mode: {self.thinking_mode.title()}")

            # Step 1: Direct query analysis if concept extraction fails
            # This is a simplification to ensure we always get results
            concepts = []
            try:
                # Try extracting concepts with the ontologist
                concepts_result = self.ontologist.define_concepts(query)
                if concepts_result and isinstance(concepts_result, dict):
                    # Extract concepts from various categories
                    for category in ["molecular_components", "cellular_processes", 
                                  "regulatory_mechanisms", "developmental_context"]:
                        if category in concepts_result:
                            concepts.extend(concepts_result[category])
            except Exception as e:
                print(f"Concept extraction error: {str(e)}")
                # Fallback: Extract key terms from the query itself
                concepts = [term.strip().lower() for term in query.split() 
                            if len(term) > 4 and term.lower() not in 
                            ['what', 'how', 'why', 'when', 'where', 'which', 'there', 'their']]
                concepts = list(set(concepts))  # Remove duplicates

            # Ensure we have at least some concepts
            if not concepts:
                # Default concepts based on common biomedical terms
                concepts = ["immune", "pathway", "regulation", "signaling", "development"]

            print(f"Analyzing with concepts: {concepts}")

            # Step 2: Graph-based Analysis
            analysis_result = self.kg_reasoner.analyze_mechanism_path(
                query, 
                concepts,
                novelty_score=novelty_score,
                include_established=include_established
            )

            # Ensure we have a valid result
            if not analysis_result or not isinstance(analysis_result, dict):
                # Generate a default response
                print("Analysis failed, generating default response")
                return self.llm_manager._generate_default_response(query)

            # Return the analysis results
            return {
                "primary_analysis": analysis_result.get("primary_analysis", {}),
                "validation": analysis_result.get("validation", "No validation available"),
                "confidence_score": analysis_result.get("confidence_score", 0.5),
                "graph_analysis": analysis_result.get("graph_analysis", {})
            }

        except Exception as e:
            print(f"Error in analysis: {str(e)}")
            # Return a default response in case of any error
            return self.llm_manager._generate_default_response(query)

    def analyze_mechanism_with_debate(self, query: str, novelty_score: float = 0.5) -> Dict:
        """
        Perform scientific analysis using the debate-driven methodology
        This implements the "generate, debate, and evolve" approach from Coscientist

        Args:
            query: Scientific query to analyze
            novelty_score: Target novelty level (0: established, 1: novel)

        Returns:
            A comprehensive scientific analysis refined through multi-agent debate
        """
        try:
            print(f"Starting debate-driven analysis of query: {query}")
            print(f"Novelty score: {novelty_score}")
            print(f"Using thinking mode: {self.thinking_mode.title()}")

            # Step 1: Extract concepts
            concepts = []
            try:
                # Extract concepts with the ontologist
                concepts_result = self.ontologist.define_concepts(query)
                if concepts_result and isinstance(concepts_result, dict):
                    # Extract concepts from various categories
                    for category in ["molecular_components", "cellular_processes", 
                                  "regulatory_mechanisms", "developmental_context"]:
                        if category in concepts_result:
                            concepts.extend(concepts_result[category])

                # Ensure we have meaningful concepts
                if not concepts:
                    # Fallback: Extract key terms from the query
                    concepts = [term.strip().lower() for term in query.split() 
                                if len(term) > 4 and term.lower() not in 
                                ['what', 'how', 'why', 'when', 'where', 'which', 'there', 'their']]
                    concepts = list(set(concepts))  # Remove duplicates
            except Exception as e:
                print(f"Concept extraction error in debate analysis: {str(e)}")
                # Default concepts for fallback
                concepts = ["immune", "pathway", "regulation", "signaling", "development"]

            print(f"Debate analysis with concepts: {concepts}")

            # Step 2: Run the multi-agent debate
            debate_result = self.debate_orchestrator.orchestrate_debate(
                query,
                concepts,
                novelty_score=novelty_score
            )

            # Step 3: Optional - Validate with knowledge graph if needed
            # This could be added for additional scientific grounding

            # Return the debate-refined analysis
            return debate_result

        except Exception as e:
            print(f"Error in debate-driven analysis: {str(e)}")
            return self.llm_manager._generate_default_response(query)