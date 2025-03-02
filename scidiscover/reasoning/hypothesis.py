from typing import List, Dict
from .llm_manager import LLMManager
from ..knowledge.pubtator import PubTatorClient

class HypothesisGenerator:
    def __init__(self):
        self.llm_manager = LLMManager()
        self.pubtator = PubTatorClient()
        
    def generate(self, topic: str) -> Dict:
        """
        Generate scientific hypotheses based on the given topic
        """
        prompt = f"""
        Generate a scientific hypothesis about {topic}. Consider:
        1. Current scientific knowledge
        2. Potential causal relationships
        3. Testable predictions
        4. Research implications

        Format the response as a JSON object with the following structure:
        {{
            "hypothesis": "main hypothesis statement",
            "supporting_concepts": ["list of related concepts"],
            "predictions": ["testable predictions"],
            "research_directions": ["suggested research directions"]
        }}
        """
        
        hypothesis = self.llm_manager.generate_response(prompt)
        
        # Fact check the hypothesis
        fact_check = self.pubtator.fact_check(hypothesis["hypothesis"])
        
        hypothesis["fact_check"] = fact_check
        return hypothesis
    
    def evaluate_hypothesis(self, hypothesis: str) -> Dict:
        """
        Evaluate a given hypothesis for scientific merit
        """
        evaluation_prompt = f"""
        Evaluate the following scientific hypothesis:
        {hypothesis}
        
        Consider:
        1. Scientific validity
        2. Testability
        3. Novelty
        4. Potential impact
        
        Provide the evaluation in JSON format.
        """
        
        return self.llm_manager.analyze_scientific_text(evaluation_prompt)
