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
                # Structured system prompt
                system_prompt = """You are a molecular biology expert. Your task is to analyze scientific queries and provide detailed insights.
When responding:
1. Keep your response focused and well-structured
2. Ensure all JSON fields are properly formatted
3. Provide comprehensive scientific details
"""
                # Build message with clear JSON structure
                message_content = f"""{system_prompt}

Analyze this query and provide insights:
{prompt}

Return your analysis as a valid JSON object with this exact structure:
{{
    "primary_analysis": {{
        "pathways": [
            "Clear description of each molecular pathway"
        ],
        "genes": [
            {{
                "name": "GENE_SYMBOL",
                "role": "Detailed description of gene's role"
            }}
        ],
        "mechanisms": "Comprehensive mechanism description",
        "timeline": [
            "Key temporal events"
        ],
        "evidence": [
            "Supporting experimental evidence"
        ],
        "implications": [
            "Clinical implications"
        ]
    }},
    "validation": "Analysis validation summary",
    "confidence_score": 0.85
}}"""

                try:
                    # Make API request
                    response = self.anthropic_client.messages.create(
                        model=ANTHROPIC_MODEL,
                        max_tokens=4000,
                        messages=[{"role": "user", "content": message_content}],
                        temperature=0.1
                    )

                    # Extract content
                    content = response.content[0].text if hasattr(response, 'content') and response.content else ""
                    if not content:
                        return {} if response_format == "json" else ""

                    # Handle JSON format
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

                            # Parse and validate JSON
                            result = json.loads(content.strip())
                            if not isinstance(result, dict):
                                return {}

                            # Validate required structure
                            if "primary_analysis" not in result:
                                return {}

                            primary = result["primary_analysis"]
                            if not isinstance(primary, dict):
                                return {}

                            # Return valid response
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
                    temperature=0.1
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

        prompt = f"""Analyze this scientific text and provide insights:

Text: {text}

Return your analysis as a valid JSON object with these fields:
- concepts: List of key scientific concepts
- relationships: List of concept relationships
- hypotheses: List of potential hypotheses
- implications: List of research implications"""

        response = self.generate_response(
            prompt,
            model_preference="anthropic",
            response_format="json"
        )

        return response if isinstance(response, dict) else {}