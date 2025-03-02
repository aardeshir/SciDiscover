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
                # Build basic prompt
                base_prompt = """You are a scientific analysis expert specializing in molecular biology.
Your task is to analyze the provided query and return a response following the exact format specified.
Format your response as a valid JSON object, nothing else."""

                # Add JSON structure for response format
                if response_format == "json":
                    format_guide = """
Your response must be a valid JSON object with exactly these fields:
{
    "primary_analysis": {
        "pathways": ["Detailed pathway descriptions"],
        "genes": [
            {"name": "GENE_NAME", "role": "Detailed description of gene's role"}
        ],
        "mechanisms": "Comprehensive mechanism description",
        "timeline": ["Key temporal events"],
        "evidence": ["Supporting experimental evidence"],
        "implications": ["Clinical and therapeutic implications"]
    },
    "validation": "Validation analysis",
    "confidence_score": 0.85
}"""
                    final_prompt = f"{base_prompt}\n\n{format_guide}\n\nQuery to analyze:\n{prompt}"
                else:
                    final_prompt = f"{base_prompt}\n\nQuery to analyze:\n{prompt}"

                # Make API request
                try:
                    print("Sending request to Claude...")
                    response = self.anthropic_client.messages.create(
                        model=ANTHROPIC_MODEL,
                        max_tokens=4000,
                        messages=[{"role": "user", "content": final_prompt}],
                        temperature=0.1
                    )

                    # Extract and validate content
                    content = response.content[0].text if hasattr(response, 'content') and response.content else ""
                    if not content:
                        print("Empty response from Claude")
                        return {}

                    # Handle JSON parsing
                    if response_format == "json":
                        try:
                            result = json.loads(content)
                            if not isinstance(result, dict):
                                print("Response is not a dictionary")
                                return {}

                            if "primary_analysis" not in result:
                                print("Missing primary_analysis field")
                                return {}

                            return result

                        except json.JSONDecodeError as e:
                            print(f"JSON parsing error: {str(e)}")
                            print(f"Failed content: {content[:200]}...")
                            return {}

                    return content

                except Exception as e:
                    print(f"Claude API error: {str(e)}")
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

        except Exception as e:
            print(f"Error in generate_response: {str(e)}")
            return {} if response_format == "json" else ""

    def analyze_scientific_text(self, text: str) -> Dict[str, Any]:
        """Analyze scientific text for key concepts"""
        if not text:
            return {}

        prompt = f"""Analyze this scientific text and extract key insights.
Format your response as a valid JSON object with these sections:
1. Key concepts
2. Relationships between concepts
3. Potential hypotheses
4. Research implications

Text: {text}"""

        response = self.generate_response(
            prompt,
            model_preference="anthropic",
            response_format="json"
        )

        return response if isinstance(response, dict) else {}