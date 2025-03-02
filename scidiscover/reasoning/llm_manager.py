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
        # The newest Anthropic model is "claude-3-5-sonnet-20241022" which was released October 22, 2024
        # Use the most advanced model available for scientific analysis
        self.anthropic_model = ANTHROPIC_MODEL
        print(f"Initialized LLM manager with Anthropic model: {self.anthropic_model}")

    def generate_response(self, prompt: str, model_preference: str = "openai", response_format: str = "text") -> Union[str, Dict]:
        """Generate response using specified LLM"""
        try:
            print(f"\nGenerating response with {model_preference}...")
            print(f"Using model: {self.anthropic_model if model_preference == 'anthropic' else OPENAI_MODEL}")
            print(f"Prompt: {prompt[:500]}...")  # Print first 500 chars of prompt for debugging

            if model_preference == "anthropic":
                # Format messages for Claude API
                messages = [
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]

                print(f"Sending request to Claude with model: {self.anthropic_model}")
                response = self.anthropic_client.messages.create(
                    model=self.anthropic_model,
                    max_tokens=4000,
                    messages=messages
                )

                # Extract content from response
                content = response.content[0].text if hasattr(response, 'content') and response.content else ""

                print(f"\nRaw Anthropic response length: {len(content)}")
                print(f"Response preview: {content[:500]}...")  # Debug log first 500 chars

                # JSON parsing handling
                if response_format == "json":
                    try:
                        # Strip markdown code blocks if present
                        if "```json" in content:
                            json_content = content.split("```json")[1].split("```")[0].strip()
                        elif "```" in content:
                            json_parts = content.split("```")
                            json_content = json_parts[1] if len(json_parts) > 1 else content
                        else:
                            json_content = content.strip()

                        # Try to parse the JSON
                        json_response = json.loads(json_content)
                        print(f"Successfully parsed JSON, keys: {list(json_response.keys() if isinstance(json_response, dict) else [])}")
                        return json_response
                    except json.JSONDecodeError as e:
                        print(f"JSON parsing error: {e}")
                        print(f"Failed content: {content[:1000]}...")  # Show more context for debugging
                        # Return an empty dict for graceful degradation
                        return {
                            "error": f"JSON parsing error: {str(e)}"
                        }
                return content

            elif model_preference == "openai":
                print(f"Sending request to OpenAI with model: {OPENAI_MODEL}")
                messages = [
                    {
                        "role": "system",
                        "content": "You are a scientific analysis assistant specialized in molecular biology. Always provide clear, accurate responses."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]

                response = self.openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    response_format={"type": "json_object"} if response_format == "json" else None,
                    temperature=0.3  # Lower temperature for more precise scientific responses
                )

                content = response.choices[0].message.content
                print(f"\nOpenAI response: {content[:500]}...")

                if response_format == "json":
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError as e:
                        print(f"JSON parsing error: {e}")
                        return {
                            "error": f"JSON parsing error: {str(e)}"
                        }
                return content

            return "" if response_format == "text" else {}
        except Exception as e:
            print(f"Error in LLM response generation: {str(e)}")
            return {} if response_format == "json" else ""

    def analyze_scientific_query(self, query: str, concepts: list, novelty_score: float = 0.5) -> Dict[str, Any]:
        """
        Scientific analysis specialized function for more reliable Claude responses
        """
        print(f"Analyzing scientific query with {len(concepts)} concepts and novelty score {novelty_score}")

        # Create a structured prompt for scientific analysis
        prompt = f"""
        Analyze this scientific query for a molecular biology discovery platform:
        Query: {query}

        Relevant concepts: {', '.join(concepts)}
        Novelty preference: {novelty_score} (0: established knowledge, 1: cutting-edge research)

        Please provide a comprehensive scientific analysis including:
        1. Key molecular pathways involved
        2. Important genes and their roles
        3. Detailed explanation of mechanisms
        4. Temporal progression of events
        5. Supporting experimental evidence
        6. Clinical and therapeutic implications

        Format your response as a structured JSON with these keys:
        - pathways: Array of important pathways
        - genes: Array of objects with name and role properties
        - mechanisms: Detailed explanation of mechanisms
        - timeline: Array of temporal events
        - evidence: Array of supporting evidence points
        - implications: Clinical and therapeutic implications
        - confidence_score: A number between 0 and 1 representing confidence

        Focus on scientific accuracy and clarity.
        """

        try:
            # Use the anthropic model directly for scientific analysis
            messages = [{"role": "user", "content": prompt}]

            print(f"Sending specialized scientific analysis request to Claude")
            response = self.anthropic_client.messages.create(
                model=self.anthropic_model,
                max_tokens=4000,
                messages=messages
            )

            content = response.content[0].text if hasattr(response, 'content') and response.content else ""
            print(f"Received scientific analysis response of length: {len(content)}")

            # Extract JSON from the response
            try:
                # Handle possible markdown formatting
                if "```json" in content:
                    json_content = content.split("```json")[1].split("```")[0].strip()
                elif "```" in content:
                    json_parts = content.split("```")
                    json_content = json_parts[1] if len(json_parts) > 1 else content
                else:
                    json_content = content.strip()

                result = json.loads(json_content)
                print(f"Successfully parsed scientific analysis JSON with keys: {list(result.keys())}")
                return result
            except json.JSONDecodeError as e:
                print(f"Error parsing scientific analysis JSON: {e}")
                print(f"Response content: {content[:1000]}...")

                # Create a fallback structured response
                return {
                    "pathways": [],
                    "genes": [],
                    "mechanisms": f"Error processing analysis: {str(e)}",
                    "timeline": [],
                    "evidence": [],
                    "implications": "Analysis failed due to formatting issues",
                    "confidence_score": 0.0
                }
        except Exception as e:
            print(f"Scientific analysis error: {str(e)}")
            return {
                "pathways": [],
                "genes": [],
                "mechanisms": f"Analysis error: {str(e)}",
                "timeline": [],
                "evidence": [],
                "implications": "Analysis failed due to technical error",
                "confidence_score": 0.0
            }