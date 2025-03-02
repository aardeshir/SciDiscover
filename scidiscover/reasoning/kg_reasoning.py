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
            if not query or not concepts:
                return self._create_error_response("Invalid input parameters")

            # Very simple prompt structure
            prompt = f"""Return a JSON object analyzing this molecular mechanism:
Query: {query}
Concepts: {', '.join(concepts)}
Novelty: {novelty_score}
Include Known: {include_established}

Required fields:
{{
    "primary_analysis": {{
        "pathways": ["pathway descriptions"],
        "genes": [
            {{"name": "gene name", "role": "role description"}}
        ],
        "mechanisms": "mechanism description",
        "timeline": ["temporal events"],
        "evidence": ["evidence"],
        "implications": ["implications"]
    }},
    "validation": "validation text",
    "confidence_score": number between 0 and 1
}}
"""

            analysis = self.llm_manager.generate_response(
                prompt,
                model_preference="anthropic",
                response_format="json",
                enable_thinking=enable_thinking
            )

            if not isinstance(analysis, dict):
                return self._create_error_response("Invalid response format")

            primary = analysis.get("primary_analysis", {})
            if not isinstance(primary, dict):
                return self._create_error_response("Missing analysis structure")

            # Return validated response
            return {
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

        except Exception as e:
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

Provide a validation analysis as JSON with these fields:
- supported_claims: List of claims supported by evidence
- missing_evidence: List of gaps in evidence
- alternative_mechanisms: List of alternative explanations
- confidence_score: Validation confidence (0-1)"""

            validation = self.llm_manager.generate_response(
                prompt,
                model_preference="anthropic",
                response_format="json"
            )

            if isinstance(validation, dict):
                return validation
            return self._create_error_response("Failed to validate hypothesis")

        except Exception as e:
            return self._create_error_response(f"Validation error: {str(e)}")