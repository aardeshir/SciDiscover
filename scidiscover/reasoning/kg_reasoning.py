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

            # Build clear, structured prompt
            analysis_prompt = f"""Analyze the molecular mechanisms and pathways for this scientific query.

Query: {query}

Key Concepts to Consider:
{', '.join(concepts)}

Analysis Parameters:
- Novelty Score: {novelty_score} (0-1 scale, higher means more novel discoveries)
- Include Established Mechanisms: {include_established}

Focus on:
1. Molecular pathways and their interactions
2. Gene regulation and expression patterns
3. Temporal sequence of events
4. Supporting experimental evidence
5. Clinical and therapeutic implications

Provide your detailed scientific analysis, ensuring accuracy and completeness."""

            print("Sending analysis request...")
            analysis = self.llm_manager.generate_response(
                analysis_prompt,
                model_preference="anthropic",
                response_format="json",
                enable_thinking=enable_thinking
            )

            print(f"Received analysis response type: {type(analysis)}")
            if not isinstance(analysis, dict):
                return self._create_error_response("Invalid response format")

            primary = analysis.get("primary_analysis", {})
            if not isinstance(primary, dict):
                return self._create_error_response("Invalid analysis structure")

            # Build response with strict validation
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

            # Validate result structure
            if not result["primary_analysis"]["pathways"]:
                print("Warning: No pathways found in analysis")
            if not result["primary_analysis"]["genes"]:
                print("Warning: No genes found in analysis")
            if result["primary_analysis"]["mechanisms"] == "No mechanism analysis available":
                print("Warning: No mechanism description available")
            if not result["primary_analysis"]["timeline"]:
                print("Warning: No temporal events found")
            if not result["primary_analysis"]["evidence"]:
                print("Warning: No supporting evidence found")
            if not result["primary_analysis"]["implications"]:
                print("Warning: No implications found")

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

Analyze the evidence support and provide assessment."""

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