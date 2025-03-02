"""LLM Manager for handling API interactions"""
import os
from openai import OpenAI
from anthropic import Anthropic
from typing import Dict, Any, Optional, Union
import json
from scidiscover.config import OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENAI_MODEL, ANTHROPIC_MODEL

class LLMManager:
    def __init__(self):
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)

    def generate_response(self, prompt: str, model_preference: str = "openai", 
                         response_format: str = "text", enable_thinking: bool = True) -> Union[str, Dict]:
        """Generate response using specified LLM"""
        try:
            if model_preference == "anthropic":
                # Basic prompt structure
                final_prompt = """Analyze this query and return ONLY a valid JSON response.
No other text, just the JSON object.

Query: {prompt}
""".format(prompt=prompt)

                response = self.anthropic_client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=4000,
                    messages=[{"role": "user", "content": final_prompt}],
                    temperature=0.1
                )

                content = response.content[0].text if hasattr(response, 'content') and response.content else ""
                if not content:
                    return {} if response_format == "json" else ""

                if response_format == "json":
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return {}
                return content

            elif model_preference == "openai":
                response = self.openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=[
                        {
                            "role": "system",
                            "content": "You are a scientific analysis assistant."
                        },
                        {
                            "role": "user",
                            "content": prompt
                        }
                    ],
                    response_format={"type": "json_object"} if response_format == "json" else None,
                    temperature=0.3
                )

                content = response.choices[0].message.content
                if response_format == "json":
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError:
                        return {}
                return content

        except Exception:
            return {} if response_format == "json" else ""

    def analyze_scientific_text(self, text: str) -> Dict[str, Any]:
        """Analyze scientific text for key concepts"""
        if not text:
            return {}

        prompt = f"""Analyze this scientific text and extract key insights.
Text: {text}

Provide your analysis as JSON with these fields:
- concepts: List of key scientific concepts
- relationships: List of concept relationships
- hypotheses: List of potential hypotheses
- implications: List of research implications
"""

        response = self.generate_response(
            prompt,
            model_preference="anthropic",
            response_format="json",
            enable_thinking=True
        )

        return response if isinstance(response, dict) else {}