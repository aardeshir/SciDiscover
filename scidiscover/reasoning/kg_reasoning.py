"""Knowledge Graph Reasoning Agent"""
from typing import Dict, List, Optional
from ..knowledge.kg_coi import KGCOIManager
from .llm_manager import LLMManager
import json

class KGReasoningAgent:
    def __init__(self, llm_manager: LLMManager):
        self.kg_manager = KGCOIManager()
        self.llm_manager = llm_manager

    def analyze_mechanism_path(self, query: str, concepts: List[str], 
                             novelty_score: float = 0.5, 
                             include_established: bool = True,
                             enable_thinking: bool = True) -> Dict:
        """Analyze molecular mechanisms using graph path exploration"""
        try:
            # Validate inputs
            if not query or not concepts:
                return self._create_error_response("Missing required inputs")

            # Build analysis prompt
            analysis_prompt = f"""Analyze these molecular mechanisms in detail:

Scientific Query: {query}

Key Concepts: {', '.join(concepts)}

Analysis Parameters:
- Novelty Score: {novelty_score} (0-1 scale, higher means more novel/recent discoveries)
- Include Established Mechanisms: {include_established}

Provide a comprehensive analysis including:
1. Key molecular pathways and their interactions
2. Gene regulation and expression patterns
3. Temporal sequence of events
4. Supporting experimental evidence
5. Clinical and therapeutic implications

Focus on scientific accuracy and mechanistic details."""

            # Get analysis from LLM
            analysis = self.llm_manager.generate_response(
                analysis_prompt,
                model_preference="anthropic",
                response_format="json",
                enable_thinking=enable_thinking
            )

            # Validate response structure
            if not isinstance(analysis, dict):
                return self._create_error_response("Invalid response format")

            primary = analysis.get("primary_analysis", {})
            if not isinstance(primary, dict):
                return self._create_error_response("Invalid analysis structure")

            # Build validated response
            result = {
                "primary_analysis": {
                    "pathways": primary.get("pathways", []),
                    "genes": primary.get("genes", []),
                    "mechanisms": primary.get("mechanisms", "No mechanism analysis available"),
                    "timeline": primary.get("timeline", []),
                    "evidence": primary.get("evidence", []),
                    "implications": primary.get("implications", [])
                },
                "validation": analysis.get("validation", "No validation available"),
                "confidence_score": float(analysis.get("confidence_score", 0))
            }

            # Verify content
            print("Validating analysis content...")
            if not result["primary_analysis"]["pathways"]:
                print("Warning: No pathways found")
            if not result["primary_analysis"]["genes"]:
                print("Warning: No genes found")
            if not result["primary_analysis"]["mechanisms"] or result["primary_analysis"]["mechanisms"] == "No mechanism analysis available":
                print("Warning: No mechanism description")

            return result

        except Exception as e:
            print(f"Error in mechanism analysis: {str(e)}")
            return self._create_error_response(str(e))

    def _create_error_response(self, error_message: str) -> Dict:
        """Helper to create consistent error responses"""
        return {
            "error": error_message,
            "primary_analysis": {
                "pathways": [],
                "genes": [],
                "mechanisms": "Analysis failed",
                "timeline": [],
                "evidence": [],
                "implications": []
            },
            "validation": "Analysis failed",
            "confidence_score": 0
        }

    def validate_hypothesis(self, hypothesis: Dict) -> Dict:
        """Validate hypothesis using knowledge graph"""
        try:
            if not isinstance(hypothesis, dict):
                return self._create_error_response("Invalid hypothesis format")

            prompt = f"""Validate this scientific hypothesis:
{json.dumps(hypothesis, indent=2)}

Provide validation analysis including:
1. Supported claims
2. Missing evidence
3. Alternative mechanisms
4. Confidence assessment"""

            validation = self.llm_manager.generate_response(
                prompt,
                model_preference="anthropic",
                response_format="json"
            )

            return validation if isinstance(validation, dict) else self._create_error_response("Failed to validate hypothesis")

        except Exception as e:
            return self._create_error_response(f"Validation error: {str(e)}")