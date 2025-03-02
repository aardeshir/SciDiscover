import os
from openai import OpenAI
from anthropic import Anthropic
from typing import Dict, Any
from scidiscover.config import OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENAI_MODEL, ANTHROPIC_MODEL

class LLMManager:
    def __init__(self):
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate_response(self, prompt: str, model_preference: str = "openai") -> str:
        """
        Generate response using specified LLM
        """
        try:
            if model_preference == "openai":
                response = self.openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[{"role": "user", "content": prompt}],
                    temperature=0.7
                )
                return response.choices[0].message.content

            elif model_preference == "anthropic":
                response = self.anthropic_client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=1000,
                    messages=[{
                        "role": "user",
                        "content": prompt
                    }]
                )
                return response.content

            return ""

        except Exception as e:
            print(f"Error in LLM response generation: {e}")
            return ""

    def analyze_scientific_text(self, text: str) -> Dict[str, Any]:
        """
        Analyze scientific text for key concepts and relationships
        """
        prompt = f"""
        Analyze the following scientific text and extract:
        1. Key concepts
        2. Relationships between concepts
        3. Potential hypotheses
        4. Research implications

        Text: {text}

        Provide the analysis in JSON format.
        """

        response = self.openai_client.chat.completions.create(
            model=OPENAI_MODEL,
            messages=[{"role": "user", "content": prompt}],
            response_format={"type": "json_object"}
        )

        return response.choices[0].message.content