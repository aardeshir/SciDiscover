"""
Specialized agents for scientific discovery and analysis
Based on SciAgents architecture (Ghafarollahi & Buehler, 2024)
"""
from typing import Dict, List, Optional
from .llm_manager import LLMManager
import json

class OntologistAgent:
    """Defines key concepts and relationships"""
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    def define_concepts(self, query: str) -> Dict:
        """Analyze query and identify key biological concepts"""
        prompt = f"""
        Analyze this scientific query for key molecular and cellular concepts:
        {query}

        Extract and structure the key concepts into the following categories:
        1. Core molecular and cellular components
        2. Key biological processes
        3. Regulatory mechanisms
        4. Temporal and developmental contexts

        Format your response as a JSON object with this exact structure:
        {{
            "molecular_components": [
                "List of specific molecules, proteins, genes involved in early life antibiotic treatment and immune system development"
            ],
            "cellular_processes": [
                "List of key biological processes affected by early antibiotic exposure"
            ],
            "regulatory_mechanisms": [
                "List of control mechanisms and pathways involved in immune development"
            ],
            "developmental_context": [
                "List of relevant developmental stages and temporal factors"
            ]
        }}

        Focus on scientific accuracy and mechanistic details.
        """

        print("\nOntologist analyzing concepts...")
        response = self.llm_manager.generate_response(prompt, "anthropic", "json")
        print(f"Ontologist response type: {type(response)}")
        print(f"Ontologist response: {json.dumps(response, indent=2)[:200]}...")

        if not isinstance(response, dict) or not response:
            print("Error: Invalid response from Ontologist")
            return {}

        return response

class ScientistAgent:
    """Generates scientific hypotheses"""
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    def generate_hypothesis(self, concepts: Dict) -> Dict:
        """Generate detailed scientific hypothesis"""
        # Handle different input formats for flexibility in debate
        if "original_hypothesis" in concepts and "critique" in concepts:
            # This is a rebuttal request during debate
            return self._generate_rebuttal(concepts)
        elif "refined_hypothesis" in concepts and "critique" in concepts:
            # This is also a rebuttal scenario
            return self._generate_rebuttal(concepts)
        else:
            # Standard hypothesis generation
            return self._generate_initial_hypothesis(concepts)

    def _generate_initial_hypothesis(self, concepts: Dict) -> Dict:
        """Generate initial scientific hypothesis"""
        prompt = f"""
        Based on these biological concepts:
        {json.dumps(concepts, indent=2)}

        Generate a detailed scientific hypothesis explaining the molecular mechanisms.
        Focus on early life antibiotic treatment's influence on immune system development.

        Include:
        1. Specific signaling pathways
        2. Gene regulatory networks
        3. Temporal sequences
        4. Causal relationships
        5. Supporting evidence

        Format your response as a JSON object with this exact structure:
        {{
            "hypothesis": "Clear statement of the main hypothesis",
            "mechanisms": {{
                "pathways": [
                    "List of specific signaling pathways involved"
                ],
                "genes": [
                    {{
                        "name": "Gene name",
                        "role": "Detailed mechanistic role"
                    }}
                ],
                "regulation": [
                    "Key regulatory mechanisms"
                ],
                "timeline": [
                    "Temporal sequence of events"
                ]
            }},
            "evidence": [
                "Supporting experimental evidence"
            ]
        }}
        """

        print("\nScientist generating hypothesis...")
        response = self.llm_manager.generate_response(prompt, "anthropic", "json")
        print(f"Scientist response: {json.dumps(response, indent=2)[:200]}...")

        if not isinstance(response, dict) or not response:
            print("Error: Invalid response from Scientist")
            return {}

        return response

    def _generate_rebuttal(self, context: Dict) -> Dict:
        """Generate rebuttal to critique during debate"""
        # Determine which hypothesis to use
        hypothesis = context.get("refined_hypothesis", context.get("original_hypothesis", {}))
        critique = context.get("critique", {})

        prompt = f"""
        Based on this scientific hypothesis:
        {json.dumps(hypothesis, indent=2)}

        And this critique:
        {json.dumps(critique, indent=2)}

        Generate a detailed rebuttal and improved hypothesis that:
        1. Addresses the key limitations identified
        2. Incorporates the suggested improvements
        3. Maintains valid points from the original hypothesis
        4. Adds new supporting evidence where needed
        5. Enhances the mechanistic explanation

        Format your response as a JSON object with the same structure as the original hypothesis,
        but with improvements addressing the critique.
        """

        print("\nScientist generating rebuttal...")
        response = self.llm_manager.generate_response(prompt, "anthropic", "json")

        if not isinstance(response, dict) or not response:
            print("Error: Invalid response from Scientist rebuttal")
            return hypothesis  # Return original as fallback

        return response

class ExpanderAgent:
    """Expands and refines research proposals"""
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    def expand_hypothesis(self, hypothesis: Dict) -> Dict:
        """Expand and refine hypothesis based on context"""
        # Handle combined context for debate
        if "original_hypothesis" in hypothesis and "critique" in hypothesis:
            # This is a refinement request during debate
            original = hypothesis.get("original_hypothesis", {})
            critique = hypothesis.get("critique", {})

            prompt = f"""
            Expand and refine this research hypothesis based on critique:

            Original Hypothesis:
            {json.dumps(original, indent=2)}

            Critique:
            {json.dumps(critique, indent=2)}

            Address these aspects:
            1. Fill gaps identified in the critique
            2. Add additional molecular pathways
            3. Explore cross-talk between pathways
            4. Include cellular compartments involved
            5. Consider systems-level effects
            6. Add potential therapeutic targets

            Format as JSON with this structure:
            {{
                "expanded_mechanisms": {{
                    "additional_pathways": ["list of related pathways"],
                    "pathway_interactions": ["mechanistic interactions"],
                    "cellular_compartments": ["involved compartments"],
                    "system_effects": ["broader physiological impacts"]
                }},
                "therapeutic_implications": ["potential interventions"],
                "research_priorities": ["key areas for investigation"]
            }}
            """
        else:
            # Standard expansion
            prompt = f"""
            Expand and refine this research hypothesis:
            {json.dumps(hypothesis, indent=2)}

            Consider:
            1. Additional molecular pathways
            2. Cross-talk between pathways
            3. Cellular compartments involved
            4. Systems-level effects
            5. Potential therapeutic targets

            Format as JSON with this structure:
            {{
                "expanded_mechanisms": {{
                    "additional_pathways": ["list of related pathways"],
                    "pathway_interactions": ["mechanistic interactions"],
                    "cellular_compartments": ["involved compartments"],
                    "system_effects": ["broader physiological impacts"]
                }},
                "therapeutic_implications": ["potential interventions"],
                "research_priorities": ["key areas for investigation"]
            }}
            """

        print("\nExpander refining hypothesis...")
        response = self.llm_manager.generate_response(prompt, "anthropic", "json")

        if not isinstance(response, dict) or not response:
            print("Error: Invalid response from Expander")
            return {}

        return response

class CriticAgent:
    """Reviews and validates scientific analyses"""
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager

    def review_hypothesis(self, hypothesis: Dict) -> Dict:
        """Critically evaluate hypothesis"""
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

        print("\nCritic evaluating hypothesis...")
        response = self.llm_manager.generate_response(prompt, "anthropic", "json")

        if not isinstance(response, dict) or not response:
            print("Error: Invalid response from Critic")
            return {}

        return response