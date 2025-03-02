"""
Specialized agents for scientific discovery and analysis
"""
from typing import Dict, List, Optional
from .llm_manager import LLMManager
import json

class OntologistAgent:
    """Defines and structures scientific concepts and relationships"""
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    def define_concepts(self, query: str) -> Dict:
        prompt = f"""
        Analyze this scientific query and identify key biological concepts:
        {query}

        Structure your response to include:
        1. Core molecular and cellular components
        2. Key biological processes
        3. Regulatory mechanisms
        4. Temporal and developmental contexts

        Format as JSON with this structure:
        {{
            "molecular_components": ["list of molecules, proteins, genes"],
            "cellular_processes": ["list of biological processes"],
            "regulatory_mechanisms": ["list of control mechanisms"],
            "developmental_context": ["list of developmental stages or conditions"]
        }}
        """
        response = self.llm_manager.generate_response(prompt, "anthropic", "json")
        return response if isinstance(response, dict) else {}

class ScientistAgent:
    """Generates and validates scientific hypotheses"""
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    def generate_hypothesis(self, concepts: Dict) -> Dict:
        prompt = f"""
        Based on these biological concepts:
        {json.dumps(concepts, indent=2)}

        Generate a detailed scientific hypothesis explaining the molecular mechanisms.

        Consider:
        1. Specific signaling pathways
        2. Gene regulatory networks
        3. Temporal sequences
        4. Causal relationships
        5. Supporting evidence from literature

        Format as JSON with this structure:
        {{
            "hypothesis": "Main hypothesis statement",
            "mechanisms": {{
                "pathways": ["involved signaling pathways"],
                "genes": [
                    {{"name": "gene name", "role": "mechanistic role"}}
                ],
                "regulation": ["regulatory mechanisms"],
                "timeline": ["temporal sequence of events"]
            }},
            "predictions": ["testable predictions"],
            "evidence": ["supporting literature evidence"]
        }}
        """
        response = self.llm_manager.generate_response(prompt, "anthropic", "json")
        return response if isinstance(response, dict) else {}

class CriticAgent:
    """Reviews and validates scientific analyses"""
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    def review_hypothesis(self, hypothesis: Dict) -> Dict:
        prompt = f"""
        Critically evaluate this scientific hypothesis:
        {json.dumps(hypothesis, indent=2)}

        Consider:
        1. Scientific rigor and mechanistic detail
        2. Evidence quality and completeness
        3. Alternative explanations
        4. Potential gaps or limitations
        5. Suggested experimental validations

        Format as JSON with this structure:
        {{
            "evaluation": {{
                "strengths": ["list of strong points"],
                "limitations": ["list of limitations"],
                "gaps": ["knowledge gaps identified"],
                "alternatives": ["alternative mechanisms"]
            }},
            "validation": {{
                "experiments": ["suggested validation experiments"],
                "predictions": ["testable predictions"],
                "controls": ["necessary controls"]
            }},
            "confidence_score": 0.95  # 0-1 score
        }}
        """
        response = self.llm_manager.generate_response(prompt, "anthropic", "json")
        return response if isinstance(response, dict) else {}