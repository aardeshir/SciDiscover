"""
Debate Orchestrator for scientific hypothesis refinement
Based on the interactive debate methodology from Google's AI Coscientist
"""
from typing import Dict, List, Optional, Callable
from .llm_manager import LLMManager
from .agents import OntologistAgent, ScientistAgent, ExpanderAgent, CriticAgent
import json
import datetime
import re

class DebateOrchestrator:
    """
    Orchestrates a multi-agent debate to refine scientific hypotheses
    Implements the "generate, debate, and evolve" methodology
    """
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        self.ontologist = OntologistAgent(llm_manager)
        self.scientist = ScientistAgent(llm_manager)
        self.expander = ExpanderAgent(llm_manager)
        self.critic = CriticAgent(llm_manager)
        self.debate_history = []
        self.debate_rounds = 3
        self.update_callback = None  # Callback for real-time updates

    def set_update_callback(self, callback: Callable):
        """
        Set a callback function to be called when there are new debate updates

        Args:
            callback: A function that takes a debate entry dictionary as input
        """
        self.update_callback = callback
        print("Debate update callback registered")

    def orchestrate_debate(self, query: str, concepts: List[str], novelty_score: float = 0.5) -> Dict:
        """
        Run a multi-agent debate to refine a scientific hypothesis

        Args:
            query: The scientific question to analyze
            concepts: Key concepts identified in the query
            novelty_score: Target novelty level (0-1)

        Returns:
            A refined scientific analysis after multiple debate rounds
        """
        print(f"Starting scientific debate on: {query}")
        print(f"With concepts: {concepts}")
        print(f"Targeting novelty level: {novelty_score}")

        # Initial hypothesis generation by scientist
        hypothesis = self._generate_initial_hypothesis(query, concepts)

        # Track the best hypothesis and its score
        best_hypothesis = hypothesis
        best_score = self._evaluate_hypothesis(hypothesis)

        print(f"Initial hypothesis generated with score: {best_score}")
        self._add_to_debate_history("ScientistAgent", "initial_hypothesis", hypothesis)

        # Run multiple rounds of debate
        for round_num in range(1, self.debate_rounds + 1):
            print(f"\n=== Starting debate round {round_num} ===")

            # Critic challenges the hypothesis
            critique = self._generate_critique(hypothesis)
            self._add_to_debate_history("CriticAgent", "critique", critique)
            print(f"Critic has challenged the hypothesis with {len(critique.get('evaluation', {}).get('limitations', []))} limitations")

            # Expander refines based on critique
            refined_hypothesis = self._refine_hypothesis(hypothesis, critique)
            self._add_to_debate_history("ExpanderAgent", "refinement", refined_hypothesis)
            print(f"Expander has refined the hypothesis with {len(refined_hypothesis.get('expanded_mechanisms', {}).get('additional_pathways', []))} new pathways")

            # Scientist rebuts and further improves
            rebuttal = self._generate_rebuttal(refined_hypothesis, critique)
            self._add_to_debate_history("ScientistAgent", "rebuttal", rebuttal)
            print(f"Scientist has provided a rebuttal and improvements")

            # Create a merged hypothesis from the debate
            hypothesis = self._merge_hypotheses(refined_hypothesis, rebuttal)

            # Evaluate the new hypothesis
            current_score = self._evaluate_hypothesis(hypothesis)
            print(f"Round {round_num} hypothesis score: {current_score}")

            # Track the best hypothesis
            if current_score > best_score:
                best_hypothesis = hypothesis
                best_score = current_score
                print(f"New best hypothesis found! Score: {best_score}")

        # Final synthesis by integrating the best hypothesis
        final_analysis = self._synthesize_final_analysis(query, best_hypothesis, best_score)
        print(f"Debate complete. Final analysis produced with confidence score: {final_analysis.get('confidence_score', 0)}")

        return final_analysis

    def _generate_initial_hypothesis(self, query: str, concepts: List[str]) -> Dict:
        """Generate initial hypothesis from the scientist agent"""
        print("Generating initial hypothesis...")

        # Create a structured context for the scientist
        context = {
            "molecular_components": concepts[:10],  # Limit to prevent token overflow
            "cellular_processes": concepts[10:20] if len(concepts) > 10 else [],
            "regulatory_mechanisms": concepts[20:30] if len(concepts) > 20 else [],
            "developmental_context": concepts[30:40] if len(concepts) > 30 else []
        }

        return self.scientist.generate_hypothesis(context)

    def _generate_critique(self, hypothesis: Dict) -> Dict:
        """Generate critique from the critic agent"""
        return self.critic.review_hypothesis(hypothesis)

    def _refine_hypothesis(self, hypothesis: Dict, critique: Dict) -> Dict:
        """Refine hypothesis based on critique"""
        # Combine hypothesis with critique for context
        combined_context = {
            "original_hypothesis": hypothesis,
            "critique": critique
        }

        return self.expander.expand_hypothesis(combined_context)

    def _generate_rebuttal(self, refined_hypothesis: Dict, critique: Dict) -> Dict:
        """Generate rebuttal and improvements from the scientist"""
        # Structure a rebuttal request
        rebuttal_context = {
            "refined_hypothesis": refined_hypothesis,
            "critique": critique,
            "rebuttal_requested": True
        }

        # Use the scientist to generate improvements
        return self.scientist.generate_hypothesis(rebuttal_context)

    def _merge_hypotheses(self, hypothesis1: Dict, hypothesis2: Dict) -> Dict:
        """Merge two hypotheses, keeping the strongest elements of each"""
        prompt = f"""
        Merge these two scientific hypotheses into a unified, stronger hypothesis:

        Hypothesis 1: {json.dumps(hypothesis1, indent=2)}

        Hypothesis 2: {json.dumps(hypothesis2, indent=2)}

        Create a unified hypothesis that:
        1. Incorporates the strongest elements from both
        2. Resolves any contradictions
        3. Maintains scientific accuracy
        4. Increases explanatory power

        Format your response as a structured JSON with the same schema as the input hypotheses.
        """

        merged = self.llm_manager.generate_response(prompt, "anthropic", "json")
        if isinstance(merged, str):
            try:
                merged = json.loads(merged)
            except:
                print("Failed to parse merged hypothesis JSON")
                # Return a combination of both as a fallback
                merged = {**hypothesis1, **hypothesis2}

        return merged

    def _evaluate_hypothesis(self, hypothesis: Dict) -> float:
        """Evaluate the hypothesis and return a score from 0-1"""
        evaluation_prompt = f"""
        Evaluate this scientific hypothesis for strength and validity:

        {json.dumps(hypothesis, indent=2)}

        Assess on these dimensions:
        1. Scientific rigor (0-1)
        2. Mechanistic detail (0-1)
        3. Evidence support (0-1)
        4. Internal consistency (0-1)
        5. Explanatory power (0-1)

        Return only a single float representing the overall score (0-1).
        """

        response = self.llm_manager.generate_response(evaluation_prompt, "anthropic", "text")

        # Extract floating point score from response
        try:
            # First try to find a float in the response
            if isinstance(response, str):
                score_match = re.search(r"(\d+\.\d+)", response)
                if score_match:
                    score = float(score_match.group(1))
                    return min(1.0, max(0.0, score))  # Ensure within 0-1

                # If that fails, try to interpret the whole response as a float
                try:
                    score = float(response.strip())
                    return min(1.0, max(0.0, score))
                except ValueError:
                    print("Failed to parse hypothesis evaluation score")
                    return 0.5
            else:
                return 0.5
        except Exception as e:
            # Default score if parsing fails
            print(f"Failed to parse hypothesis evaluation score: {str(e)}")
            return 0.5

    def _synthesize_final_analysis(self, query: str, best_hypothesis: Dict, score: float) -> Dict:
        """Create the final analysis from the best hypothesis"""
        synthesis_prompt = f"""
        Create a comprehensive scientific analysis based on this refined hypothesis:

        Query: {query}

        Best Hypothesis: {json.dumps(best_hypothesis, indent=2)}

        Structure your response as a JSON with these keys:
        - primary_analysis: {{
            "pathways": ["list of important pathways"],
            "genes": [{{"name": "gene name", "role": "detailed role"}}],
            "mechanisms": "Detailed explanation of mechanisms",
            "timeline": ["temporal sequence of events"],
            "evidence": ["supporting evidence points"],
            "implications": "Clinical and therapeutic implications"
        }}
        - validation: "Validation statement",
        - confidence_score: {score}
        """

        final_analysis = self.llm_manager.generate_response(synthesis_prompt, "anthropic", "json")
        if isinstance(final_analysis, str):
            try:
                final_analysis = json.loads(final_analysis)
            except:
                print("Failed to parse final analysis JSON")
                # Create a default structure
                final_analysis = {
                    "primary_analysis": {
                        "pathways": best_hypothesis.get("mechanisms", {}).get("pathways", []),
                        "genes": best_hypothesis.get("mechanisms", {}).get("genes", []),
                        "mechanisms": best_hypothesis.get("hypothesis", ""),
                        "timeline": best_hypothesis.get("mechanisms", {}).get("timeline", []),
                        "evidence": best_hypothesis.get("evidence", []),
                        "implications": best_hypothesis.get("expanded_mechanisms", {}).get("therapeutic_implications", [])
                    },
                    "validation": "Analysis validated through multi-agent scientific debate",
                    "confidence_score": score
                }

        return final_analysis

    def _add_to_debate_history(self, agent_name: str, action_type: str, content: Dict) -> None:
        """Add an entry to the debate history"""
        entry = {
            "agent": agent_name,
            "action": action_type,
            "content": content,
            "timestamp": datetime.datetime.now().isoformat()
        }

        # Add to local history
        self.debate_history.append(entry)

        # Call the update callback if available
        if self.update_callback:
            try:
                self.update_callback(entry)
                print(f"Real-time update sent for {agent_name} - {action_type}")
            except Exception as e:
                print(f"Error in debate update callback: {str(e)}")

    def get_debate_history(self) -> List[Dict]:
        """Get the debate history"""
        return self.debate_history