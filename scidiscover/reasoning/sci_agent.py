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

        Format the response as a structured JSON with the following fields:
        - pathways: List of relevant signaling pathways
        - genes: List of genes with their roles
        - mechanisms: Detailed molecular mechanisms
        - timeline: Temporal sequence of events
        - evidence: Key experimental findings
        - implications: Clinical/therapeutic relevance

        Focus on scientific accuracy and detail.
        """

        # Use Claude for primary analysis
        mechanism_analysis = self.llm_manager.generate_response(
            analysis_prompt, 
            model_preference="anthropic"
        )

        # Validate with OpenAI
        validation_prompt = f"""
        Validate and enhance this molecular mechanism analysis:
        {mechanism_analysis}

        Check for:
        1. Scientific accuracy
        2. Missing key pathways
        3. Additional relevant genes
        4. Recent discoveries
        """

        validation = self.llm_manager.generate_response(
            validation_prompt,
            model_preference="openai"
        )

        try:
            # Combine and structure the analysis
            combined_analysis = {
                "primary_analysis": json.loads(mechanism_analysis),
                "validation": json.loads(validation),
                "confidence_score": self._calculate_confidence(
                    mechanism_analysis,
                    validation
                )
            }

            return combined_analysis

        except json.JSONDecodeError:
            print("Error parsing LLM response as JSON")
            return {
                "error": "Failed to parse analysis",
                "raw_analysis": mechanism_analysis,
                "raw_validation": validation
            }

    def _calculate_confidence(self, analysis: str, validation: str) -> float:
        """
        Calculate confidence score based on agreement between analyses
        """
        validation_prompt = f"""
        Calculate a confidence score (0-1) for these scientific analyses:
        Analysis 1: {analysis}
        Analysis 2: {validation}

        Consider:
        1. Agreement on key mechanisms
        2. Support from literature
        3. Completeness of explanation
        4. Scientific rigor

        Return only the numeric score.
        """

        score = self.llm_manager.generate_response(
            validation_prompt,
            model_preference="anthropic"
        )

        try:
            return float(score)
        except ValueError:
            return 0.5  # Default score if parsing fails
