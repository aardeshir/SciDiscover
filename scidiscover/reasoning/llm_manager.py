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
                # Set up system message
                system_message = {
                    "role": "system",
                    "content": "You are a scientific analysis expert specializing in molecular biology and biochemistry. Provide detailed, accurate analysis of scientific queries."
                }

                user_message = {
                    "role": "user",
                    "content": prompt
                }

                # Configure thinking parameters
                thinking_config = None
                if enable_thinking:
                    thinking_config = {
                        "type": "enabled",
                        "budget_tokens": 6000  # Allocate tokens for extended thinking
                    }

                # Make API request with extended thinking
                try:
                    print(f"Using Claude model: {ANTHROPIC_MODEL} with extended thinking: {enable_thinking}")
                    response = self.anthropic_client.messages.create(
                        model=ANTHROPIC_MODEL,
                        max_tokens=8000,
                        messages=[system_message, user_message],
                        temperature=0.1,
                        thinking=thinking_config
                    )

                    # Extract main content
                    content = response.content[0].text if hasattr(response, 'content') and response.content else ""

                    # Get thinking process if available
                    thinking_content = response.thinking if hasattr(response, 'thinking') else None
                    print(f"Thinking content available: {thinking_content is not None}")

                    if not content:
                        print("Error: Empty response from Claude")
                        return {} if response_format == "json" else ""

                    # Handle JSON format
                    if response_format == "json":
                        try:
                            # Clean up response for JSON parsing
                            json_content = content.strip()
                            if "```json" in json_content:
                                json_content = json_content.split("```json")[1].split("```")[0].strip()
                            elif "```" in json_content:
                                json_content = json_content.split("```")[1].split("```")[0].strip()

                            # Parse JSON
                            result = json.loads(json_content)

                            # Add thinking process if available
                            if enable_thinking and thinking_content:
                                result["thinking_process"] = thinking_content

                            return result

                        except json.JSONDecodeError as e:
                            print(f"JSON parsing error: {str(e)}")
                            # If JSON parsing fails, try to be more lenient
                            try:
                                # Find JSON-like structure in the response
                                if "{" in content and "}" in content:
                                    start = content.find("{")
                                    end = content.rfind("}") + 1
                                    json_str = content[start:end]
                                    result = json.loads(json_str)

                                    if enable_thinking and thinking_content:
                                        result["thinking_process"] = thinking_content

                                    return result
                            except Exception as inner_e:
                                print(f"Failed to extract JSON: {str(inner_e)}")
                                return {}

                            return {}

                    # For text format, simply return content with thinking if available
                    if enable_thinking and thinking_content:
                        return f"Thinking process:\n{thinking_content}\n\nFinal response:\n{content}"
                    return content

                except Exception as e:
                    print(f"Claude API error: {str(e)}")
                    return {} if response_format == "json" else ""

            elif model_preference == "openai":
                # OpenAI integration
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

        except Exception as e:
            print(f"Error in generate_response: {str(e)}")
            return {} if response_format == "json" else ""

    def analyze_scientific_text(self, text: str) -> Dict[str, Any]:
        """Analyze scientific text for key concepts"""
        if not text:
            return {}

        prompt = f"""Analyze this scientific text and extract key insights:

Text: {text}

Provide a comprehensive analysis that includes:
1. Key molecular and biological concepts
2. Relationships between identified concepts
3. Potential scientific hypotheses
4. Research implications and applications

Your analysis should be detailed, scientifically accurate, and structured clearly."""

        response = self.generate_response(
            prompt,
            model_preference="anthropic",
            response_format="json",
            enable_thinking=True
        )

        return response if isinstance(response, dict) else {}