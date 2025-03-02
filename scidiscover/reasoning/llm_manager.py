import os
from openai import OpenAI
from anthropic import Anthropic
from typing import Dict, Any, Optional
import json
from scidiscover.config import OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENAI_MODEL, ANTHROPIC_MODEL

class LLMManager:
    def __init__(self):
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate_response(self, prompt: str, model_preference: str = "openai", response_format: str = "text") -> str:
        """
        Generate response using specified LLM
        """
        try:
            if model_preference == "openai":
                messages = [{"role": "user", "content": prompt}]

                # Add JSON format instruction if needed
                if response_format == "json":
                    messages.insert(0, {
                        "role": "system",
                        "content": "You are a scientific analysis assistant. Always respond with valid JSON."
                    })

                response = self.openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    response_format={"type": "json_object"} if response_format == "json" else None
                )
                return response.choices[0].message.content

            elif model_preference == "anthropic":
                system_prompt = "You are a scientific analysis assistant." 
                if response_format == "json":
                    system_prompt += " Always respond with valid JSON."
                    prompt += "\nFormat your response as a valid JSON object."

                response = self.anthropic_client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=4000,
                    messages=[
                        {
                            "role": "system",
                            "content": system_prompt
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ]
                )
                return response.content[0].text

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

        Return a JSON object with the following structure:
        {{
            "concepts": ["list of key concepts"],
            "relationships": [
                {{"source": "concept1", "target": "concept2", "relationship": "description"}}
            ],
            "hypotheses": ["list of potential hypotheses"],
            "implications": ["list of research implications"]
        }}
        """

        response = self.generate_response(prompt, model_preference="anthropic", response_format="json")

        try:
            return json.loads(response)
        except json.JSONDecodeError as e:
            print(f"Error parsing JSON response: {e}")
            print(f"Raw response: {response}")
            return {
                "error": "Failed to parse analysis",
                "concepts": [],
                "relationships": [],
                "hypotheses": [],
                "implications": []
            }