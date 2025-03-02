from typing import Dict, List, Optional
from ..knowledge.pubtator import PubTatorClient
from .llm_manager import LLMManager
import json

class SciAgent:
    def __init__(self):
        self.llm_manager = LLMManager()
        self.pubtator = PubTatorClient()

    def analyze_mechanism(self, query: str) -> Dict:
        """
        Perform deep scientific analysis of molecular mechanisms
        """
        analysis_prompt = f"""
        Analyze the following scientific query and provide a detailed molecular mechanism analysis:
        Query: {query}

        Please provide a comprehensive analysis including:
        1. Key molecular pathways involved
        2. Specific genes and their roles
        3. Temporal sequence of events
        4. Known regulatory mechanisms
        5. Supporting experimental evidence
        6. Cellular components involved
        7. Potential therapeutic implications

        Return a JSON object with the following structure:
        {{
            "pathways": ["List of relevant signaling pathways"],
            "genes": [
                {{
                    "name": "Gene name",
                    "role": "Detailed role in the mechanism"
                }}
            ],
            "mechanisms": "Detailed description of molecular mechanisms",
            "timeline": ["Temporal sequence of events"],
            "evidence": ["Key experimental findings"],
            "implications": "Clinical and therapeutic relevance"
        }}

        Focus on scientific accuracy and detail.
        """

        # Use Claude for primary analysis
        mechanism_analysis = self.llm_manager.generate_response(
            analysis_prompt, 
            model_preference="anthropic",
            response_format="json"
        )

        try:
            primary_analysis = json.loads(mechanism_analysis)
        except json.JSONDecodeError:
            primary_analysis = {
                "error": "Failed to parse primary analysis",
                "raw_response": mechanism_analysis
            }
            return primary_analysis

        # Validate with OpenAI
        validation_prompt = f"""
        Validate and enhance this molecular mechanism analysis:
        {json.dumps(primary_analysis, indent=2)}

        Check for:
        1. Scientific accuracy
        2. Missing key pathways
        3. Additional relevant genes
        4. Recent discoveries

        Return a JSON object with your validation findings.
        """

        validation = self.llm_manager.generate_response(
            validation_prompt,
            model_preference="openai",
            response_format="json"
        )

        try:
            validation_data = json.loads(validation)
            confidence_score = self._calculate_confidence(primary_analysis, validation_data)

            return {
                "primary_analysis": primary_analysis,
                "validation": validation_data,
                "confidence_score": confidence_score
            }

        except json.JSONDecodeError:
            return {
                "primary_analysis": primary_analysis,
                "error": "Failed to parse validation",
                "raw_validation": validation
            }

    def _calculate_confidence(self, analysis: Dict, validation: Dict) -> float:
        """
        Calculate confidence score based on agreement between analyses
        """
        validation_prompt = f"""
        Calculate a confidence score (0-1) for these scientific analyses:
        Analysis 1: {json.dumps(analysis)}
        Analysis 2: {json.dumps(validation)}

        Consider:
        1. Agreement on key mechanisms
        2. Support from literature
        3. Completeness of explanation
        4. Scientific rigor

        Return a JSON object with the structure: {{"confidence": float}}
        """

        score_response = self.llm_manager.generate_response(
            validation_prompt,
            model_preference="anthropic",
            response_format="json"
        )

        try:
            score_data = json.loads(score_response)
            return float(score_data.get("confidence", 0.5))
        except (json.JSONDecodeError, ValueError):
            return 0.5  # Default score if parsing fails