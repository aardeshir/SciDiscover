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
            # Input validation
            if not query or not concepts:
                return self._create_error_response("Please provide a query and concepts for analysis")

            # Build clear analysis prompt
            prompt = f"""Analyze this molecular mechanism in detail:

Query: {query}
Key Concepts: {', '.join(concepts)}

Analysis Parameters:
- Novelty Level: {novelty_score} (0-1 scale, higher means more novel/recent)
- Include Known Mechanisms: {include_established}

Provide a comprehensive scientific analysis with:
1. Detailed molecular pathways and interactions
2. Gene regulation and expression patterns
3. Temporal sequence of events
4. Supporting experimental evidence
5. Clinical and therapeutic implications"""

            # Get analysis from LLM
            analysis = self.llm_manager.generate_response(
                prompt,
                model_preference="anthropic",
                response_format="json",
                enable_thinking=enable_thinking
            )

            # Validate response structure
            if not isinstance(analysis, dict):
                return self._create_error_response("Invalid analysis format received")

            # Extract and validate primary analysis
            primary = analysis.get("primary_analysis", {})
            if not isinstance(primary, dict):
                return self._create_error_response("Invalid analysis structure")

            # Build response with validation
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

            # Validate content
            if not any([
                result["primary_analysis"]["pathways"],
                result["primary_analysis"]["genes"],
                result["primary_analysis"]["mechanisms"] != "No mechanism analysis available"
            ]):
                return self._create_error_response("No valid analysis content generated")

            return result

        except Exception as e:
            return self._create_error_response(f"Analysis error: {str(e)}")

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

            # Simple validation prompt
            prompt = f"""Validate this scientific hypothesis:
{json.dumps(hypothesis, indent=2)}

Provide validation including:
1. Evidence support assessment
2. Gaps in current evidence
3. Alternative mechanisms
4. Confidence level"""

            validation = self.llm_manager.generate_response(
                prompt,
                model_preference="anthropic",
                response_format="json"
            )

            return validation if isinstance(validation, dict) else self._create_error_response("Failed to validate hypothesis")

        except Exception as e:
            return self._create_error_response(f"Validation error: {str(e)}")