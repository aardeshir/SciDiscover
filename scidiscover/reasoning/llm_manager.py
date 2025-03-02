import os
from openai import OpenAI
from anthropic import Anthropic
from typing import Dict, Any, Optional, Union
import json
from scidiscover.config import (
    OPENAI_API_KEY, ANTHROPIC_API_KEY, OPENAI_MODEL, 
    ANTHROPIC_MODEL, ANTHROPIC_MAX_TOKENS_HIGH, ANTHROPIC_MAX_TOKENS_LOW,
    ANTHROPIC_THINKING_BUDGET_HIGH, ANTHROPIC_THINKING_BUDGET_LOW, ANTHROPIC_BETA_HEADER
)

class LLMManager:
    def __init__(self, high_demand_mode=True):
        self.openai_client = OpenAI(api_key=OPENAI_API_KEY)
        self.anthropic_client = Anthropic(api_key=ANTHROPIC_API_KEY)
        # The newest Anthropic model is "claude-3-7-sonnet-20250219" which was released February 19, 2025
        # This model supports extended thinking capabilities
        self.anthropic_model = ANTHROPIC_MODEL

        # Set token limits based on the selected mode
        self.high_demand_mode = high_demand_mode
        self.set_thinking_mode(high_demand_mode)

        print(f"Initialized LLM manager with Anthropic model: {self.anthropic_model}")
        print(f"Thinking mode: {'High-Demand' if high_demand_mode else 'Low-Demand'}")
        print(f"Max tokens: {self.max_tokens}, Thinking budget: {self.thinking_budget}")

    def set_thinking_mode(self, high_demand=True):
        """Set the thinking mode for extended thinking capabilities"""
        self.high_demand_mode = high_demand
        if high_demand:
            self.max_tokens = ANTHROPIC_MAX_TOKENS_HIGH
            self.thinking_budget = ANTHROPIC_THINKING_BUDGET_HIGH
        else:
            self.max_tokens = ANTHROPIC_MAX_TOKENS_LOW
            self.thinking_budget = ANTHROPIC_THINKING_BUDGET_LOW

    def generate_response(self, prompt: str, model_preference: str = "anthropic", response_format: str = "text") -> Union[str, Dict]:
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

                # Use streaming for long-running operations to avoid timeouts
                full_content = ""
                with self.anthropic_client.beta.messages.stream(
                    model=self.anthropic_model,
                    max_tokens=self.max_tokens,
                    messages=messages,
                    thinking={
                        "type": "enabled",
                        "budget_tokens": self.thinking_budget
                    },
                    betas=[ANTHROPIC_BETA_HEADER]
                ) as stream:
                    # Initialize to store thinking process
                    thinking_text = ""

                    print("Streaming response from Claude...")
                    for chunk in stream:
                        # Handle content chunks
                        if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                            # Print progress indicator
                            print(".", end="", flush=True)
                            full_content += chunk.delta.text

                        # Handle thinking chunks
                        if hasattr(chunk, 'thinking') and chunk.thinking:
                            thinking_text += chunk.thinking
                            print("T", end="", flush=True)  # 'T' indicates thinking updated

                    print()  # New line after progress indicators

                    # Log thinking process if available
                    if thinking_text:
                        print(f"\nExtended thinking process captured ({len(thinking_text)} chars)")
                        thinking_excerpt = thinking_text[:1000] + "..." if len(thinking_text) > 1000 else thinking_text
                        print(thinking_excerpt)

                        # Save thinking for debugging if needed
                        with open("claude_thinking_log.txt", "w") as f:
                            f.write(thinking_text)

                content = full_content
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
        print(f"Using thinking mode: {'High-Demand' if self.high_demand_mode else 'Low-Demand'}")
        print(f"Max tokens: {self.max_tokens}, Thinking budget: {self.thinking_budget}")

        # Create a structured prompt for scientific analysis with extended thinking
        prompt = f"""
        Analyze this scientific query for a molecular biology discovery platform using your extended thinking capabilities:
        Query: {query}

        Relevant concepts: {', '.join(concepts)}
        Novelty preference: {novelty_score} (0: established knowledge, 1: cutting-edge research)

        Take advantage of your extended thinking capabilities ({self.thinking_budget} tokens) to explore:
        1. Complex causal chains and mechanisms
        2. Multi-level relationships between elements
        3. Contradictory evidence and scientific debates
        4. Alternative hypotheses and edge cases
        5. Temporal dynamics and feedback loops
        6. Scale-crossing implications (molecular to clinical)
        7. Cross-disciplinary connections and insights

        Please provide a comprehensive scientific analysis including:
        1. Key molecular pathways involved
        2. Important genes and their roles
        3. Detailed explanation of mechanisms
        4. Temporal progression of events
        5. Supporting experimental evidence
        6. Clinical and therapeutic implications
        7. Future research directions

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
            # Use streaming for Claude API call to avoid timeouts with extended thinking
            # Format messages for Claude API
            messages = [{"role": "user", "content": prompt}]

            print(f"Sending specialized scientific analysis request to Claude with extended thinking")

            # Use streaming to handle long-running requests
            full_content = ""
            thinking_text = ""

            with self.anthropic_client.beta.messages.stream(
                model=self.anthropic_model,
                max_tokens=self.max_tokens,
                messages=messages,
                thinking={
                    "type": "enabled",
                    "budget_tokens": self.thinking_budget
                },
                betas=[ANTHROPIC_BETA_HEADER]
            ) as stream:
                print("Streaming scientific analysis from Claude...")
                for chunk in stream:
                    # Handle content chunks
                    if hasattr(chunk, 'delta') and hasattr(chunk.delta, 'text'):
                        print(".", end="", flush=True)  # Show progress
                        full_content += chunk.delta.text

                    # Handle thinking chunks
                    if hasattr(chunk, 'thinking') and chunk.thinking:
                        thinking_text += chunk.thinking
                        print("T", end="", flush=True)  # 'T' for thinking

                print()  # New line after progress indicators

            # Log thinking process if available
            if thinking_text:
                print(f"Extended thinking process available ({len(thinking_text)} characters)")
                # Save thinking for debugging
                with open("claude_thinking_log.txt", "w") as f:
                    f.write(thinking_text)

            content = full_content
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

    def _generate_default_response(self, query: str) -> Dict:
        """Generate a default response structure when API calls fail"""
        print("Generating default response structure")

        # Extract what seems to be a topic from the query
        topic = query.split("?")[0] if "?" in query else query
        topic = topic.strip()

        # Create a basic response structure
        return {
            "primary_analysis": {
                "pathways": [
                    "TLR4-mediated recognition pathway",
                    "SCFA-GPCR signaling pathway",
                    "Aryl hydrocarbon receptor activation pathway"
                ],
                "genes": [
                    {"name": "FOXP3", "role": "Master regulator of regulatory T cell development"},
                    {"name": "TLR4", "role": "Pattern recognition receptor for bacterial lipopolysaccharides"},
                    {"name": "AHR", "role": "Transcription factor activated by microbial tryptophan metabolites"}
                ],
                "mechanisms": f"The {topic} involves complex interactions between host immune cells and microbiota-derived signals that calibrate immune system development during critical early life windows.",
                "timeline": [
                    "Birth and initial colonization",
                    "Establishment of core microbiome",
                    "Development of immune tolerance mechanisms",
                    "Establishment of barrier immunity"
                ],
                "evidence": [
                    "Mouse models demonstrate altered immune development following antibiotic exposure",
                    "Human cohort studies show associations between infant antibiotic exposure and immune disorders",
                    "Gnotobiotic studies reveal specific bacterial species influence immune cell populations"
                ],
                "implications": "Therapeutic approaches may include targeted probiotics, metabolite supplementation, and careful antibiotic stewardship during critical developmental windows."
            },
            "validation": "This response represents default content due to API processing limitations. Please try your query again or modify it for better results.",
            "confidence_score": 0.5
        }