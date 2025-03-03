"""
Debate orchestration module for multi-agent scientific debate.
Enhanced with Elo-based hypothesis evaluation system.
"""

import datetime
import json
import re
from typing import Dict, List, Optional, Callable, Any
import random

from .agents import OntologistAgent, ScientistAgent, ExpanderAgent, CriticAgent
from .llm_manager import LLMManager
from .elo_evaluator import HypothesisEloManager

class DebateOrchestrator:
    """
    Orchestrates multi-agent debate for scientific hypothesis generation and refinement.
    Enhanced with Elo-style hypothesis comparison and tournament evaluation.
    """
    def __init__(self, llm_manager: LLMManager):
        self.llm_manager = llm_manager
        # Core agents
        self.ontologist = OntologistAgent(llm_manager)
        self.scientist = ScientistAgent(llm_manager)
        self.expander = ExpanderAgent(llm_manager)
        self.critic = CriticAgent(llm_manager)

        # Extended specialized agents collection (dynamically selected based on query)
        self.specialized_agents = {
            "methodology": {
                "role": "Methodology Expert",
                "description": "Focuses on experimental design, statistical validity, and methodological rigor"
            },
            "domain": {
                "role": "Domain Specialist",
                "description": "Provides deep subject-matter expertise in relevant biological domains"
            },
            "statistics": {
                "role": "Statistical Analyst",
                "description": "Evaluates statistical evidence, bias, and confidence intervals"
            },
            "translational": {
                "role": "Translational Researcher",
                "description": "Focuses on clinical applications and therapeutic potential"
            },
            "evolution": {
                "role": "Evolutionary Biologist",
                "description": "Provides perspective on evolutionary constraints and advantages"
            }
        }

        # Initialize Elo-based hypothesis evaluator
        self.elo_evaluator = HypothesisEloManager(llm_manager)

        self.debate_history = []
        self.base_debate_rounds = 3
        self.update_callback = None  # Callback for real-time updates
        self.convergence_threshold = 0.8  # Threshold for debate convergence
        self.max_debate_rounds = 5  # Maximum number of rounds regardless of convergence
        self.use_elo_evaluation = False  # Whether to use Elo-based evaluation

    def set_update_callback(self, callback: Callable):
        """
        Set callback function for real-time debate updates
        Args:
            callback: A function that takes a debate history entry and processes it
        """
        self.update_callback = callback

    def enable_elo_evaluation(self, enabled: bool = True):
        """Enable or disable Elo-based hypothesis evaluation"""
        self.use_elo_evaluation = enabled
        print(f"Elo-based hypothesis evaluation {'enabled' if enabled else 'disabled'}")

    def orchestrate_debate(self, query: str, concepts: List[str], 
                         novelty_score: float = 0.5,
                         use_elo: bool = None) -> Dict:
        """
        Orchestrate multi-agent debate to generate and refine scientific hypotheses
        Args:
            query: Scientific question or topic
            concepts: List of relevant scientific concepts
            novelty_score: Target novelty level (0=established, 1=novel)
            use_elo: Whether to use Elo-based evaluation (overrides instance setting)
        Returns:
            Final analysis with debate history
        """
        if use_elo is not None:
            self.use_elo_evaluation = use_elo

        # Reset debate history
        self.debate_history = []

        # Reset hypothesis container for this debate session
        debate_hypotheses = []

        print(f"Starting scientific debate orchestration for: {query}")
        print(f"With concepts: {concepts}")
        print(f"Targeting novelty level: {novelty_score}")
        print(f"Using Elo evaluation: {self.use_elo_evaluation}")

        # Determine query complexity to set adaptive debate parameters
        query_complexity = self._evaluate_query_complexity(query, concepts)

        # Adjust debate rounds based on complexity
        target_debate_rounds = min(
            self.max_debate_rounds, 
            max(2, int(self.base_debate_rounds * query_complexity))
        )

        print(f"Query complexity: {query_complexity:.2f} - Target debate rounds: {target_debate_rounds}")

        # Select relevant specialized agents for this query
        selected_specialists = self._select_specialized_agents(query, concepts)
        print(f"Selected specialized agents: {[agent for agent in selected_specialists]}")

        # Initial hypothesis generation by scientist
        hypothesis = self._generate_initial_hypothesis(query, concepts)
        debate_hypotheses.append(hypothesis.copy())  # Store initial hypothesis

        # Evaluate initial hypothesis
        if self.use_elo_evaluation:
            # Register initial hypothesis with Elo system
            self.elo_evaluator.register_hypothesis(hypothesis)

        # Standard evaluation for backward compatibility
        best_hypothesis = hypothesis
        best_score = self._evaluate_hypothesis(hypothesis)

        print(f"Initial hypothesis generated with score: {best_score}")
        self._add_to_debate_history("ScientistAgent", "initial_hypothesis", hypothesis)

        # Run multiple rounds of debate with convergence checking
        round_num = 1
        convergence = False
        previous_score = best_score

        while round_num <= target_debate_rounds and not convergence:
            print(f"\n=== Starting debate round {round_num} ===")

            # Critic challenges the hypothesis
            critique = self._generate_critique(hypothesis, selected_specialists)
            self._add_to_debate_history("CriticAgent", "critique", critique)
            print(f"Critic has challenged the hypothesis with {len(critique.get('evaluation', {}).get('limitations', []))} limitations")

            # Expander refines the hypothesis
            refined_hypothesis = self._refine_hypothesis(hypothesis, critique)
            debate_hypotheses.append(refined_hypothesis.copy())  # Store refined hypothesis
            self._add_to_debate_history("ExpanderAgent", "refinement", refined_hypothesis)
            print(f"Expander has refined the hypothesis with {len(refined_hypothesis.get('expanded_mechanisms', {}).get('additional_pathways', []))} new pathways")

            # Specialized agent contributions if available
            if selected_specialists:
                for specialist_key in selected_specialists:
                    specialist_input = self._generate_specialist_contribution(
                        specialist_key, 
                        refined_hypothesis, 
                        critique,
                        query
                    )
                    agent_name = self.specialized_agents[specialist_key]["role"]
                    self._add_to_debate_history(agent_name, "specialist_input", specialist_input)
                    print(f"{agent_name} provided specialized input")

                    # Integrate specialist contributions
                    refined_hypothesis = self._integrate_specialist_input(
                        refined_hypothesis, 
                        specialist_input
                    )

            # Scientist rebuts and further improves
            rebuttal = self._generate_rebuttal(refined_hypothesis, critique)
            debate_hypotheses.append(rebuttal.copy())  # Store rebuttal hypothesis
            self._add_to_debate_history("ScientistAgent", "rebuttal", rebuttal)

            # Evaluate new hypothesis
            current_score = self._evaluate_hypothesis(rebuttal)
            print(f"Rebuttal hypothesis evaluated with score: {current_score}")

            # If using Elo, also compare with previous best hypothesis
            if self.use_elo_evaluation and best_hypothesis is not None:
                # Compare current hypothesis with previous best
                elo_result = self.elo_evaluator.compare_hypotheses(
                    rebuttal, best_hypothesis, query
                )

                print(f"Elo comparison - New vs Best: {elo_result['outcome_score']} (1.0 = new wins)")

                # Update best hypothesis based on Elo winner
                if elo_result['winner_id'] == self.elo_evaluator.register_hypothesis(rebuttal):
                    best_hypothesis = rebuttal
                    best_score = current_score
                    print(f"New best hypothesis based on Elo! Score: {best_score}")
            else:
                # Standard approach: update if score is better
                if current_score > best_score:
                    best_hypothesis = rebuttal
                    best_score = current_score
                    print(f"New best hypothesis found! Score: {best_score}")

            # Check for convergence (diminishing improvements)
            improvement = current_score - previous_score
            if improvement < 0.05 and round_num >= 2:
                convergence_probability = 1.0 - (improvement * 10)
                if convergence_probability > self.convergence_threshold:
                    convergence = True
                    print(f"Debate has converged with probability {convergence_probability:.2f}")

            previous_score = current_score
            round_num += 1

        # Final evaluation using Elo tournament if enabled and we have multiple hypotheses
        if self.use_elo_evaluation and len(debate_hypotheses) >= 3:
            print("\n=== Running final Elo tournament ===")
            tournament_results = self.elo_evaluator.run_tournament(
                debate_hypotheses, query, rounds=2
            )

            # Use tournament winner as final best hypothesis
            best_hypothesis = tournament_results["best_hypothesis"]
            best_score = self._evaluate_hypothesis(best_hypothesis)

            print(f"Tournament complete. Best hypothesis rating: {tournament_results['best_hypothesis_rating']}")

            # Add tournament results to debate history
            self._add_to_debate_history("Tournament", "final_evaluation", {
                "rankings": [
                    {
                        "rank": r["rank"],
                        "rating": r["rating"],
                        "hypothesis_id": r["hypothesis_id"]
                    } for r in tournament_results["rankings"]
                ]
            })

        # Final synthesis by integrating the best hypothesis
        final_analysis = self._synthesize_final_analysis(query, best_hypothesis, best_score)
        print(f"Debate complete. Final analysis produced with confidence score: {final_analysis.get('confidence_score', 0)}")

        # Add Elo leaderboard if enabled
        if self.use_elo_evaluation:
            final_analysis["elo_evaluation"] = {
                "leaderboard": self.elo_evaluator.get_leaderboard(),
                "best_hypothesis_rating": self.elo_evaluator.get_hypothesis_rating(
                    self.elo_evaluator.register_hypothesis(best_hypothesis)
                )
            }

        return final_analysis

    def _evaluate_query_complexity(self, query: str, concepts: List[str]) -> float:
        """
        Evaluate query complexity to determine debate parameters
        Returns a score from 0.5 (simple) to 2.0 (very complex)
        """
        complexity_factors = {
            "query_length": min(1.0, len(query.split()) / 50),
            "concept_count": min(1.0, len(concepts) / 20),
            "interdisciplinary": self._assess_interdisciplinary(query, concepts),
            "technical_terms": self._count_technical_terms(query) / 10
        }

        # Calculate weighted complexity score
        weights = {
            "query_length": 0.1,
            "concept_count": 0.3,
            "interdisciplinary": 0.4,
            "technical_terms": 0.2
        }

        complexity = sum(score * weights[factor] for factor, score in complexity_factors.items())
        # Scale between 0.5 and 2.0
        scaled_complexity = 0.5 + (complexity * 1.5)

        return min(2.0, scaled_complexity)

    def _assess_interdisciplinary(self, query: str, concepts: List[str]) -> float:
        """Assess interdisciplinary nature of the query"""
        domains = {
            "molecular": ["gene", "protein", "enzyme", "transcription", "binding", "receptor"],
            "cellular": ["cell", "tissue", "organelle", "differentiation", "membrane"],
            "systems": ["organ", "physiology", "homeostasis", "circulation", "nervous"],
            "ecological": ["species", "environment", "population", "ecosystem"],
            "computational": ["model", "algorithm", "simulation", "prediction"]
        }

        # Count domains represented
        domain_count = 0
        for domain, terms in domains.items():
            if any(term in query.lower() for term in terms) or \
               any(any(term in concept.lower() for term in terms) for concept in concepts):
                domain_count += 1

        # Normalize to 0-1 range
        return min(1.0, domain_count / 3)

    def _count_technical_terms(self, query: str) -> int:
        """Count technical/specialized terms in query"""
        technical_terms = [
            "pathway", "signaling", "receptor", "transcription", "translation", 
            "kinase", "phosphorylation", "methylation", "acetylation", "cytokine",
            "microbiome", "metagenome", "epigenetic", "sequencing", "enzyme"
        ]

        return sum(1 for term in technical_terms if term in query.lower())

    def _select_specialized_agents(self, query: str, concepts: List[str]) -> List[str]:
        """Select specialized agents most relevant to the query"""
        # Simple keyword-based agent selection
        agent_selection_criteria = {
            "methodology": ["method", "technique", "protocol", "experimental", "design"],
            "domain": ["mechanism", "pathway", "biology", "system", "function"],
            "statistics": ["statistical", "significance", "correlation", "causation", "evidence"],
            "translational": ["clinical", "therapy", "patient", "treatment", "disease"],
            "evolution": ["evolutionary", "conserved", "selection", "adaptation", "phylogeny"]
        }

        selected = []
        for agent_key, keywords in agent_selection_criteria.items():
            if any(kw in query.lower() for kw in keywords) or \
               any(any(kw in concept.lower() for kw in keywords) for concept in concepts):
                selected.append(agent_key)

        # Limit to at most 2 specialized agents for efficiency
        if len(selected) > 2:
            return selected[:2]
        return selected

    def _generate_initial_hypothesis(self, query: str, concepts: List[str]) -> Dict:
        """Generate initial hypothesis from the scientist agent"""
        context = {
            "query": query,
            "concepts": concepts,
            "ontology": {
                "primary_concepts": concepts[:min(3, len(concepts))],
                "related_concepts": concepts[min(3, len(concepts)):]
            }
        }

        return self.scientist.generate_hypothesis(context)

    def _generate_critique(self, hypothesis: Dict, selected_specialists: List[str] = None) -> Dict:
        """Generate critique from the critic agent with specialist focus areas"""
        critique_context = hypothesis.copy()

        # Add specialized focus areas if specialists are selected
        if selected_specialists:
            critique_context["focus_areas"] = [
                self.specialized_agents[specialist]["description"]
                for specialist in selected_specialists
            ]

        return self.critic.review_hypothesis(critique_context)

    def _generate_specialist_contribution(self, specialist_key: str, 
                                        hypothesis: Dict, critique: Dict, 
                                        query: str) -> Dict:
        """Generate specialized contribution from a domain expert agent"""
        specialist_role = self.specialized_agents[specialist_key]["role"]
        specialist_desc = self.specialized_agents[specialist_key]["description"]

        prompt = f"""
        You are a {specialist_role} who {specialist_desc}.
        Analyze this scientific hypothesis and related critique from your specialist perspective:

        Original query: {query}

        Hypothesis: {json.dumps(hypothesis, indent=2)}

        Critique: {json.dumps(critique, indent=2)}

        Provide specialized insights from your unique perspective that could strengthen the hypothesis.

        Format your response as a JSON object with these fields:
        - specialist_perspective: Your overall assessment
        - key_insights: List of specialist insights
        - suggested_improvements: Specific suggested modifications
        - relevant_methodologies: Methodologies relevant to your specialty
        - confidence_assessment: How confident you are in the hypothesis from your specialist view (0-1)
        """

        response = self.llm_manager.generate_response(prompt, "anthropic", "json")

        # Handle string or dict response
        if isinstance(response, str):
            try:
                return json.loads(response)
            except json.JSONDecodeError:
                return {"specialist_perspective": response, "key_insights": []}

        return response

    def _integrate_specialist_input(self, hypothesis: Dict, specialist_input: Dict) -> Dict:
        """Integrate specialist contributions into the hypothesis"""
        # Deep copy of hypothesis to avoid modifying the original
        enhanced = hypothesis.copy()

        # Add specialist insights if available
        if "key_insights" in specialist_input and specialist_input["key_insights"]:
            if "expanded_mechanisms" not in enhanced:
                enhanced["expanded_mechanisms"] = {}

            if "specialist_insights" not in enhanced["expanded_mechanisms"]:
                enhanced["expanded_mechanisms"]["specialist_insights"] = []

            enhanced["expanded_mechanisms"]["specialist_insights"].extend(
                specialist_input["key_insights"]
            )

        # Add methodological improvements if available
        if "suggested_improvements" in specialist_input and specialist_input["suggested_improvements"]:
            if "methodological_improvements" not in enhanced:
                enhanced["methodological_improvements"] = []

            if isinstance(specialist_input["suggested_improvements"], list):
                enhanced["methodological_improvements"].extend(specialist_input["suggested_improvements"])
            else:
                enhanced["methodological_improvements"].append(specialist_input["suggested_improvements"])

        return enhanced

    def _refine_hypothesis(self, hypothesis: Dict, critique: Dict) -> Dict:
        """Refine hypothesis based on critique"""
        return self.expander.refine_hypothesis(hypothesis, critique)

    def _generate_rebuttal(self, hypothesis: Dict, critique: Dict) -> Dict:
        """Generate rebuttal and improvements from the scientist"""
        return self.scientist.rebut_critique(hypothesis, critique)

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

    def get_elo_ratings(self) -> Dict[str, float]:
        """Get current Elo ratings for all hypotheses"""
        if not self.use_elo_evaluation:
            return {"error": "Elo evaluation not enabled"}

        return self.elo_evaluator.ratings

    def get_elo_leaderboard(self, top_n: int = 10) -> List[Dict]:
        """Get current hypothesis Elo leaderboard"""
        if not self.use_elo_evaluation:
            return [{"error": "Elo evaluation not enabled"}]

        return self.elo_evaluator.get_leaderboard(top_n)