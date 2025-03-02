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
                # Construct a clear, structured prompt
                system_message = """You are a scientific analysis expert. Analyze the given query about molecular mechanisms and provide:
1. A detailed analysis of pathways and mechanisms
2. Gene interactions and their roles
3. Supporting evidence and implications

Structure your response with clear sections."""

                final_prompt = f"""{system_message}

Here is the scientific query to analyze:
{prompt}

Your response should be a valid JSON object with this exact structure:
{{
    "primary_analysis": {{
        "pathways": [
            "Clear descriptions of molecular pathways"
        ],
        "genes": [
            {{
                "name": "GENE1",
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
            "Clinical and therapeutic implications"
        ]
    }},
    "validation": "Validation analysis",
    "confidence_score": 0.85,
    "thinking_process": "Analysis steps and reasoning"
}}

Focus on scientific accuracy and provide complete details."""

                # Get response with error handling
                try:
                    response = self.anthropic_client.messages.create(
                        model=ANTHROPIC_MODEL,
                        max_tokens=4000,
                        messages=[{"role": "user", "content": final_prompt}],
                        temperature=0.1
                    )

                    content = response.content[0].text if hasattr(response, 'content') and response.content else ""
                    if not content:
                        print("Empty response from Claude")
                        return {}

                    # Parse and validate JSON
                    if response_format == "json":
                        try:
                            result = json.loads(content)

                            # Validate required fields
                            if not isinstance(result, dict):
                                print("Response is not a dictionary")
                                return {}

                            if "primary_analysis" not in result:
                                print("Missing primary_analysis")
                                return {}

                            primary = result["primary_analysis"]
                            if not isinstance(primary, dict):
                                print("Invalid primary_analysis structure")
                                return {}

                            # Ensure all required fields exist
                            required_fields = ["pathways", "genes", "mechanisms", "timeline", "evidence", "implications"]
                            for field in required_fields:
                                if field not in primary:
                                    print(f"Missing required field: {field}")
                                    return {}

                            return result
                        except json.JSONDecodeError as e:
                            print(f"JSON parsing error: {e}")
                            return {}

                    return content

                except Exception as e:
                    print(f"Claude API error: {str(e)}")
                    return {}

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

        prompt = """Analyze this scientific text and provide insights.
Format your response as a valid JSON object with these sections:
1. Key molecular concepts
2. Relationships between concepts
3. Potential hypotheses
4. Research implications

Text: """ + text

        response = self.generate_response(
            prompt,
            model_preference="anthropic",
            response_format="json",
            enable_thinking=True
        )

        return response if isinstance(response, dict) else {}