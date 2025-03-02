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

    def generate_response(self, prompt: str, model_preference: str = "openai", response_format: str = "text") -> Union[str, Dict]:
        """Generate response using specified LLM"""
        try:
            print(f"\nGenerating response with {model_preference}...")
            print(f"Prompt: {prompt[:200]}...")  # Print first 200 chars of prompt

            if model_preference == "anthropic":
                messages = [
                    {
                        "role": "user",
                        "content": "You are a scientific research assistant trained in molecular biology and bioinformatics. "
                                 "Always provide responses in valid JSON format when requested."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ]

                response = self.anthropic_client.messages.create(
                    model=ANTHROPIC_MODEL,
                    max_tokens=4000,
                    messages=messages
                )

                # Extract content from response
                content = response.content[0].text if hasattr(response, 'content') else None
                print(f"\nRaw Claude response: {content}")

                if response_format == "json" and content:
                    try:
                        json_response = json.loads(content)
                        print(f"Parsed JSON successfully: {json.dumps(json_response, indent=2)[:200]}...")
                        return json_response
                    except json.JSONDecodeError as e:
                        print(f"JSON parsing error: {e}")
                        print(f"Failed content: {content}")
                        return {}
                return content or ""

            elif model_preference == "openai":
                messages = [{"role": "user", "content": prompt}]
                if response_format == "json":
                    messages.insert(0, {
                        "role": "system",
                        "content": "You are a scientific analysis assistant specialized in molecular biology. "
                                 "Always respond with valid JSON."
                    })

                response = self.openai_client.chat.completions.create(
                    model=OPENAI_MODEL,
                    messages=messages,
                    response_format={"type": "json_object"} if response_format == "json" else None,
                    temperature=0.3  # Lower temperature for more precise scientific responses
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