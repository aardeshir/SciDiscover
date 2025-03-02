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
        """Generate response using specified LLM with extended thinking capabilities"""
        try:
            print(f"\nGenerating response with {model_preference}...")
            print(f"Using model: {ANTHROPIC_MODEL if model_preference == 'anthropic' else OPENAI_MODEL}")
            print(f"Prompt: {prompt[:200]}...")  # Print first 200 chars of prompt

            if model_preference == "anthropic":
                thinking_prompt = """
                Use extended thinking mode to analyze this query thoroughly.
                Show your reasoning process before providing the final response.

                Consider:
                1. Key concepts and their relationships
                2. Supporting evidence and contradictions
                3. Alternative hypotheses
                4. Methodological considerations
                5. Practical implications

                Structure your response to include both:
                1. Your thinking process
                2. The final formatted answer

                Original Query:
                """ + prompt

                messages = [
                    {
                        "role": "user",
                        "content": thinking_prompt if enable_thinking else prompt
                    }
                ]

                print(f"Sending request to Claude with model: {ANTHROPIC_MODEL}")
                response = self.anthropic_client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=64000 if enable_thinking else 4000,
                    messages=messages,
                    temperature=0.3
                )

                # Extract content from response
                content = response.content[0].text if hasattr(response, 'content') else None

                if not content:
                    print("No content in Anthropic response")
                    return {} if response_format == "json" else ""

                print(f"\nRaw Anthropic response: {content[:200]}...")  # Debug log

                # Process response based on format
                if response_format == "json":
                    try:
                        # First, try to extract just the JSON part
                        if "```json" in content:
                            json_content = content.split("```json")[1].split("```")[0]
                        elif "Here's my final analysis in JSON format:" in content:
                            json_content = content.split("Here's my final analysis in JSON format:")[1]
                        else:
                            json_content = content

                        # Clean up and parse JSON
                        json_content = json_content.strip()
                        result = json.loads(json_content)

                        # Add thinking process if available
                        if enable_thinking and "THINKING PROCESS:" in content:
                            thinking = content.split("THINKING PROCESS:")[1].split("FINAL ANALYSIS:")[0].strip()
                            if isinstance(result, dict):
                                result["thinking_process"] = thinking

                        print(f"Parsed JSON successfully: {json.dumps(result, indent=2)[:200]}...")
                        return result
                    except json.JSONDecodeError as e:
                        print(f"JSON parsing error: {e}")
                        print(f"Failed content: {content}")
                        return {}
                return content

            elif model_preference == "openai":
                # OpenAI implementation remains unchanged
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
                    temperature=0.3
                )

                content = response.choices[0].message.content
                print(f"\nOpenAI response: {content[:200]}...")

                if response_format == "json":
                    try:
                        return json.loads(content)
                    except json.JSONDecodeError as e:
                        print(f"JSON parsing error: {e}")
                        return {}
                return content

        except Exception as e:
            print(f"Error in LLM response generation: {str(e)}")
            return {} if response_format == "json" else ""

    def analyze_scientific_text(self, text: str) -> Dict[str, Any]:
        """Analyze scientific text with extended thinking capabilities"""
        prompt = f"""
        Use extended thinking mode to analyze the following scientific text and extract:
        1. Key concepts
        2. Relationships between concepts
        3. Potential hypotheses
        4. Research implications

        THINKING PROCESS:
        First, I will:
        1. Identify core scientific concepts
        2. Map relationships and dependencies
        3. Consider alternative interpretations
        4. Evaluate evidence strength
        5. Assess practical applications

        Text: {text}

        Return a JSON object with the following structure:
        {{
            "thinking_process": "detailed analysis steps",
            "concepts": ["list of key concepts"],
            "relationships": [
                {{"source": "concept1", "target": "concept2", "relationship": "description"}}
            ],
            "hypotheses": ["list of potential hypotheses"],
            "implications": ["list of research implications"]
        }}
        """

        response = self.generate_response(prompt, model_preference="anthropic", 
                                       response_format="json", enable_thinking=True)
        if isinstance(response, dict):
            return response

        try:
            return json.loads(response) if isinstance(response, str) else {}
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