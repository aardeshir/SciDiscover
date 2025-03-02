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
                # Simple message template
                message = {
                    "role": "user",
                    "content": f"""You are a molecular biology expert. Analyze this query and provide detailed scientific insights.

Query: {prompt}

Return ONLY a valid JSON object with this structure:
{{
    "primary_analysis": {{
        "pathways": ["List each pathway with clear description"],
        "genes": [
            {{"name": "Gene symbol", "role": "Detailed role description"}}
        ],
        "mechanisms": "Detailed mechanism description",
        "timeline": ["Key temporal events"],
        "evidence": ["Supporting evidence"],
        "implications": ["Clinical implications"]
    }},
    "validation": "Validation summary",
    "confidence_score": 0.85
}}"""
                }

                try:
                    # Get response
                    response = self.anthropic_client.messages.create(
                        model=ANTHROPIC_MODEL,
                        max_tokens=4000,
                        messages=[message],
                        temperature=0.1
                    )

                    # Extract content
                    content = response.content[0].text if hasattr(response, 'content') and response.content else ""
                    if not content:
                        return {} if response_format == "json" else ""

                    # Parse JSON
                    if response_format == "json":
                        try:
                            # Clean up response
                            content = content.strip()
                            if content.startswith("```json"):
                                content = content.split("```json")[1]
                            if content.startswith("```"):
                                content = content.split("```")[1]
                            if content.endswith("```"):
                                content = content.rsplit("```", 1)[0]

                            # Parse JSON
                            result = json.loads(content.strip())

                            # Validate structure
                            if not isinstance(result, dict) or "primary_analysis" not in result:
                                return {}

                            return result

                        except json.JSONDecodeError:
                            return {}

                    return content

                except Exception:
                    return {} if response_format == "json" else ""

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

        prompt = f"""Analyze this scientific text and extract key insights:

Text: {text}

Return a JSON object with these sections:
- concepts: List of key concepts
- relationships: List of concept relationships
- hypotheses: List of potential hypotheses
- implications: List of research implications"""

        response = self.generate_response(
            prompt,
            model_preference="anthropic",
            response_format="json"
        )

        return response if isinstance(response, dict) else {}