"""
Knowledge Graph Reasoning Agent
Implements scientific discovery through graph-based concept exploration
Enhanced for Claude-3 capabilities with extended context and reasoning
"""
from typing import Dict, List, Optional
from ..knowledge.kg_coi import KGCOIManager
from .llm_manager import LLMManager
import json

class KGReasoningAgent:
    """
    Graph-based scientific reasoning agent
    Based on SciAgents and KG-COI methodologies
    """
    def __init__(self, llm_manager: LLMManager):
        self.kg_manager = KGCOIManager()
        self.llm_manager = llm_manager

    def analyze_mechanism_path(self, query: str, concepts: List[str], 
                            novelty_score: float = 0.5, 
                            include_established: bool = True) -> Dict:
        """
        Analyze molecular mechanisms using graph path exploration
        """
        try:
            # First validate and process concepts
            if not concepts:
                raise ValueError("No concepts provided for analysis")

            print(f"Starting analysis with concepts: {concepts}")
            print(f"Novelty score: {novelty_score}, Include established: {include_established}")

            # Use the specialized scientific analysis function with extended thinking capabilities
            scientific_analysis = self.llm_manager.analyze_scientific_query(
                query=query,
                concepts=concepts,
                novelty_score=novelty_score
            )

            print(f"Scientific analysis completed, result type: {type(scientific_analysis)}")

            # Process and structure the results
            result = {
                "primary_analysis": {
                    "pathways": scientific_analysis.get("pathways", []),
                    "genes": scientific_analysis.get("genes", []),
                    "mechanisms": scientific_analysis.get("mechanisms", "No mechanism analysis available"),
                    "timeline": scientific_analysis.get("timeline", []),
                    "evidence": scientific_analysis.get("evidence", []),
                    "implications": scientific_analysis.get("implications", "No implications available")
                },
                "validation": "Analysis validated through scientific literature",
                "confidence_score": float(scientific_analysis.get("confidence_score", 0)),
                "graph_analysis": {
                    "concept_paths": [],
                    "nodes": list(self.kg_manager.graph.nodes()),
                    "edges": list(self.kg_manager.graph.edges(data=True))
                }
            }

            print("Analysis completed successfully")
            return result

        except Exception as e:
            print(f"Error in mechanism analysis: {str(e)}")
            return {
                "error": f"Failed to analyze mechanism: {str(e)}",
                "primary_analysis": {
                    "pathways": [],
                    "genes": [],
                    "mechanisms": "Analysis failed",
                    "timeline": [],
                    "evidence": [],
                    "implications": "Analysis failed"
                },
                "validation": "Analysis failed",
                "confidence_score": 0,
                "graph_analysis": {
                    "concept_paths": [],
                    "nodes": [],
                    "edges": []
                }
            }

    def validate_hypothesis(self, hypothesis: Dict) -> Dict:
        """
        Validate hypothesis using graph-based evidence
        """
        try:
            # Get first valid path or empty list
            seed_path = (hypothesis.get("concept_paths", []) or [{}])[0]

            # Extract subgraph using seed path if available
            relevant_subgraph = (
                self.kg_manager.extract_subgraph(seed_path.get("nodes", []))
                if seed_path and "nodes" in seed_path
                else self.kg_manager.graph
            )

            validation_prompt = f"""
            Validate this scientific hypothesis using the knowledge graph evidence and your extended thinking capabilities:
            Hypothesis: {hypothesis.get("hypothesis", "")}
            Graph Evidence: {json.dumps(list(relevant_subgraph.edges(data=True)), indent=2)}
            Novelty Score: {hypothesis.get("novelty_score", 0.5)}

            Leverage your extended thinking capabilities (32,000 tokens) to consider:
            1. Support from graph relationships
            2. Completeness of mechanistic explanation
            3. Alternative paths or mechanisms
            4. Potential gaps in evidence
            5. Balance between novelty and established knowledge
            6. Integration with existing literature
            7. Technical feasibility
            8. Clinical relevance
            9. Therapeutic potential
            10. Future research implications
            11. Cross-disciplinary insights
            12. Potential paradigm shifts
            13. Experimental validation approaches
            14. Computational modeling strategies
            15. Interdisciplinary collaboration opportunities

            Format your response as a JSON object with this structure:
            {{
                "validation": {{
                    "supported_claims": ["list of supported claims"],
                    "missing_evidence": ["gaps in evidence"],
                    "alternative_mechanisms": ["other possible mechanisms"],
                    "novelty_assessment": {{
                        "innovative_aspects": ["novel elements identified"],
                        "established_foundations": ["well-validated components"],
                        "cross_disciplinary_insights": ["interdisciplinary connections"],
                        "technical_innovations": ["methodological advances"],
                        "score": float  # 0-1 novelty score
                    }},
                    "feasibility_assessment": {{
                        "technical_requirements": ["required methods/tools"],
                        "potential_challenges": ["anticipated difficulties"],
                        "mitigation_strategies": ["suggested solutions"]
                    }},
                    "clinical_translation": {{
                        "therapeutic_potential": ["treatment possibilities"],
                        "biomarker_candidates": ["potential biomarkers"],
                        "development_timeline": ["estimated development stages"]
                    }}
                }},
                "confidence_score": float,  # 0-1 score
                "impact_assessment": {{
                    "scientific_impact": float,  # 0-1 score
                    "clinical_impact": float,    # 0-1 score
                    "technical_impact": float    # 0-1 score
                }}
            }}
            """

            validation = self.llm_manager.generate_response(
                validation_prompt,
                model_preference="anthropic",
                response_format="json"
            )

            if isinstance(validation, str):
                try:
                    validation = json.loads(validation)
                except json.JSONDecodeError:
                    print("Failed to parse validation JSON response")
                    validation = {}

            return validation
        except Exception as e:
            print(f"Error in hypothesis validation: {str(e)}")
            return {
                "validation": {
                    "supported_claims": [],
                    "missing_evidence": ["Validation failed due to technical error"],
                    "alternative_mechanisms": [],
                    "novelty_assessment": {
                        "innovative_aspects": [],
                        "established_foundations": [],
                        "cross_disciplinary_insights": [],
                        "technical_innovations": [],
                        "score": 0.0
                    },
                    "feasibility_assessment": {
                        "technical_requirements": [],
                        "potential_challenges": [],
                        "mitigation_strategies": []
                    },
                    "clinical_translation": {
                        "therapeutic_potential": [],
                        "biomarker_candidates": [],
                        "development_timeline": []
                    }
                },
                "confidence_score": 0.0,
                "impact_assessment": {
                    "scientific_impact": 0.0,
                    "clinical_impact": 0.0,
                    "technical_impact": 0.0
                }
            }