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

            # Craft a detailed prompt for scientific analysis
            analysis_prompt = f"""Analyze the following molecular mechanisms query in depth:

QUERY: {query}

KEY CONCEPTS: {', '.join(concepts)}

ANALYSIS PARAMETERS:
- Novelty Level: {novelty_score} (0-1 scale where higher values indicate more recent/novel discoveries)
- Include Established Mechanisms: {include_established}

INSTRUCTIONS:
Provide a comprehensive scientific analysis that covers:
1. Key molecular pathways involved in the mechanism, with clear descriptions
2. Relevant genes and their roles in these pathways
3. Detailed description of the molecular mechanisms
4. Temporal sequence of events in the process
5. Supporting experimental evidence from literature
6. Clinical and therapeutic implications

FORMAT YOUR RESPONSE AS A VALID JSON OBJECT with the following structure:
{{
    "primary_analysis": {{
        "pathways": [
            "Description of pathway 1",
            "Description of pathway 2"
        ],
        "genes": [
            {{
                "name": "GENE1",
                "role": "Detailed description of this gene's role"
            }},
            {{
                "name": "GENE2",
                "role": "Detailed description of this gene's role"
            }}
        ],
        "mechanisms": "Comprehensive description of the molecular mechanisms",
        "timeline": [
            "First temporal event",
            "Second temporal event"
        ],
        "evidence": [
            "First piece of supporting evidence",
            "Second piece of supporting evidence"
        ],
        "implications": [
            "First clinical or therapeutic implication",
            "Second clinical or therapeutic implication"
        ]
    }},
    "validation": "Summary of how well-established this analysis is",
    "confidence_score": 0.85
}}"""

            # Get analysis with thinking enabled
            print("Sending analysis request with extended thinking...")
            analysis = self.llm_manager.generate_response(
                analysis_prompt,
                model_preference="anthropic",
                response_format="json",
                enable_thinking=enable_thinking
            )

            # Validate response structure
            if not isinstance(analysis, dict):
                print("Error: Invalid response format from LLM")
                return self._create_error_response("Invalid analysis format received")

            # Extract and validate primary analysis
            primary = analysis.get("primary_analysis", {})
            if not isinstance(primary, dict):
                print("Error: Invalid primary_analysis structure")
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
                "confidence_score": float(analysis.get("confidence_score", 0)),
                "thinking_process": analysis.get("thinking_process")
            }

            # Validate content
            if not any([
                result["primary_analysis"]["pathways"],
                result["primary_analysis"]["genes"],
                result["primary_analysis"]["mechanisms"] != "No mechanism analysis available"
            ]):
                print("Error: No valid analysis content generated")
                return self._create_error_response("No valid analysis content generated")

            return result

        except Exception as e:
            print(f"Error in analysis: {str(e)}")
            return self._create_error_response(f"Analysis error: {str(e)}")

    def _create_error_response(self, error_message: str) -> Dict:
        """Helper to create consistent error responses"""
        print(f"Creating error response: {error_message}")
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

Provide a comprehensive validation including:
1. Assessment of evidence supporting the hypothesis
2. Identification of gaps in current evidence
3. Discussion of alternative mechanisms
4. Overall confidence assessment
5. Suggestions for experimental validation"""

            validation = self.llm_manager.generate_response(
                prompt,
                model_preference="anthropic",
                response_format="json"
            )

            return validation if isinstance(validation, dict) else self._create_error_response("Failed to validate hypothesis")

        except Exception as e:
            return self._create_error_response(f"Validation error: {str(e)}")