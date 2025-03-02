from typing import Dict, List, Optional
from .llm_manager import LLMManager
from .agents import OntologistAgent, ScientistAgent, CriticAgent
import json

class SciAgent:
    """
    Orchestrates multi-agent scientific analysis and discovery
    """
    def __init__(self):
        self.llm_manager = LLMManager()
        self.ontologist = OntologistAgent(self.llm_manager)
        self.scientist = ScientistAgent(self.llm_manager)
        self.critic = CriticAgent(self.llm_manager)

    def analyze_mechanism(self, query: str) -> Dict:
        """
        Perform deep scientific analysis of molecular mechanisms
        """
        try:
            # Step 1: Ontological Analysis
            concepts = self.ontologist.define_concepts(query)
            if isinstance(concepts, str):
                concepts = json.loads(concepts)

            # Step 2: Hypothesis Generation
            hypothesis = self.scientist.generate_hypothesis(concepts)
            if isinstance(hypothesis, str):
                hypothesis = json.loads(hypothesis)

            # Step 3: Critical Review
            review = self.critic.review_hypothesis(hypothesis)
            if isinstance(review, str):
                review = json.loads(review)

            # Combine analyses
            return {
                "primary_analysis": {
                    "pathways": hypothesis["mechanisms"]["pathways"],
                    "genes": hypothesis["mechanisms"]["genes"],
                    "mechanisms": hypothesis["hypothesis"],
                    "timeline": hypothesis["mechanisms"]["timeline"],
                    "evidence": hypothesis["evidence"],
                    "implications": hypothesis["predictions"]
                },
                "validation": review["evaluation"],
                "confidence_score": review["confidence_score"]
            }

        except json.JSONDecodeError as e:
            return {
                "error": f"Failed to parse analysis: {str(e)}",
                "concepts": concepts if 'concepts' in locals() else {},
                "hypothesis": hypothesis if 'hypothesis' in locals() else {}
            }
        except Exception as e:
            return {
                "error": f"Analysis error: {str(e)}"
            }