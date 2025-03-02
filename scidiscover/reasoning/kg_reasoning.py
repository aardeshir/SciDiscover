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
        # Extract relationships between concepts
        relationships_prompt = f"""
        For these scientific concepts related to the query:
        Query: {query}
        Concepts: {', '.join(concepts)}

        Identify mechanistic relationships between concepts, considering:
        Novelty Level: {novelty_score} (0: Well-established, 1: Novel/Recent)
        Include Established Mechanisms: {include_established}

        If novelty_score is high, focus on:
        - Recent discoveries (last 2-3 years)
        - Emerging hypotheses
        - Novel interaction pathways
        - Cutting-edge experimental evidence
        - Potential breakthrough mechanisms
        - Cross-disciplinary connections
        - High-impact preliminary findings
        - Novel computational predictions
        - Emerging therapeutic targets
        - Innovative experimental approaches

        If novelty_score is low or include_established is true, include:
        - Well-validated mechanisms
        - Classical pathways
        - Foundational discoveries
        - Established experimental evidence
        - Core regulatory circuits
        - Essential molecular interactions
        - Canonical signaling cascades
        - Textbook knowledge
        - Historical breakthroughs
        - Standard therapeutic approaches

        Leverage Claude's extended reasoning to consider:
        1. Complex temporal dynamics
        2. Non-linear feedback loops
        3. Multi-scale interactions
        4. Stochastic effects
        5. Environmental influences 
        6. Epigenetic regulation
        7. Post-translational modifications
        8. Spatial organization
        9. Tissue-specific contexts
        10. Development stages
        11. Disease states
        12. Therapeutic implications

        Format your response as a JSON array of relationships with this structure:
        [
            {{
                "source": "concept1",
                "target": "concept2",
                "type": "mechanistic relationship type",
                "evidence": ["supporting evidence 1", "supporting evidence 2"],
                "novelty": float,  # 0-1 score indicating how novel this relationship is
                "confidence": float,  # 0-1 score indicating evidence strength
                "temporal_dynamics": ["temporal sequence details"],
                "regulatory_circuits": ["regulatory mechanism details"],
                "spatial_context": ["spatial organization details"],
                "clinical_relevance": ["therapeutic implications"]
            }}
        ]
        """
        try:
            relationships = self.llm_manager.generate_response(
                relationships_prompt,
                model_preference="anthropic",
                response_format="json"
            )

            if isinstance(relationships, str):
                relationships = json.loads(relationships)

            # Build knowledge graph
            self.kg_manager.build_concept_graph(concepts, relationships)

            # Sample concept paths
            paths = []
            if len(concepts) > 1:  # Only try to find paths if we have at least 2 concepts
                for i in range(len(concepts)-1):
                    for j in range(i+1, len(concepts)):
                        concept_paths = self.kg_manager.sample_concept_paths(
                            concepts[i],
                            concepts[j]
                        )
                        if concept_paths:  # Only extend if we found paths
                            paths.extend(concept_paths)

            # If no paths found, create a basic path structure
            if not paths:
                paths = [{"nodes": concepts[:2] if len(concepts) > 1 else concepts,
                         "edges": [],
                         "type": "direct"}]

            # Generate hypothesis from paths
            hypothesis_prompt = f"""
            Based on these concept relationship paths:
            {json.dumps(paths, indent=2)}

            Generate a detailed scientific hypothesis explaining the molecular mechanisms.
            Novelty Level: {novelty_score} (0: Well-established, 1: Novel/Recent)
            Include Established Mechanisms: {include_established}

            Leverage Claude's extended thinking capabilities (64000 tokens) to provide:
            1. Comprehensive mechanistic explanations
            2. Detailed molecular interactions
            3. Temporal dynamics analysis
            4. Multi-scale integration
            5. Clinical implications
            6. Future research directions

            Consider:
            1. Sequential progression through each path
            2. Mechanistic connections between concepts
            3. Supporting experimental evidence
            4. Potential regulatory interactions
            5. Cell-type specific effects
            6. Tissue microenvironment
            7. Systems-level impact
            8. Therapeutic potential
            9. Biomarker implications
            10. Drug development opportunities

            If novelty_score is high, emphasize:
            - Recently discovered mechanisms
            - Novel pathway interactions
            - Emerging therapeutic targets
            - Cutting-edge experimental approaches
            - Cross-disciplinary insights
            - Computational predictions
            - High-risk, high-reward hypotheses
            - Innovative therapeutic strategies
            - Breakthrough technologies
            - Paradigm-shifting concepts

            If novelty_score is low or include_established is true, include:
            - Well-validated mechanisms
            - Classical regulatory pathways
            - Established experimental evidence
            - Core molecular machinery
            - Essential biological processes
            - Standard therapeutic approaches
            - Validated biomarkers
            - Proven drug targets
            - Historical discoveries
            - Clinical standards

            Format your response as a JSON object with this structure:
            {{
                "hypothesis": "detailed hypothesis statement",
                "mechanisms": {{
                    "pathways": ["key pathways identified"],
                    "interactions": ["mechanistic interactions"],
                    "regulation": ["regulatory mechanisms"],
                    "temporal_dynamics": ["temporal progression details"],
                    "spatial_organization": ["spatial context information"],
                    "cell_type_effects": ["cell-specific mechanisms"],
                    "tissue_context": ["tissue-level implications"]
                }},
                "evidence": {{
                    "experimental": ["experimental evidence"],
                    "computational": ["computational predictions"],
                    "clinical": ["clinical observations"]
                }},
                "predictions": ["testable predictions"],
                "novelty_scores": {{
                    "pathways": float,  # Average novelty of pathways
                    "evidence": float,  # Average novelty of evidence
                    "concepts": float,  # Average novelty of concepts
                    "overall": float    # Overall hypothesis novelty
                }},
                "therapeutic_implications": {{
                    "drug_targets": ["potential therapeutic targets"],
                    "biomarkers": ["candidate biomarkers"],
                    "treatment_strategies": ["proposed interventions"]
                }},
                "future_directions": {{
                    "key_questions": ["important open questions"],
                    "technical_needs": ["required technological advances"],
                    "validation_approaches": ["suggested validation methods"]
                }}
            }}
            """

            hypothesis = self.llm_manager.generate_response(
                hypothesis_prompt,
                model_preference="anthropic",
                response_format="json"
            )

            if isinstance(hypothesis, str):
                hypothesis = json.loads(hypothesis)

            return {
                "concept_paths": paths,
                "hypothesis": hypothesis,
                "knowledge_graph": {
                    "nodes": list(self.kg_manager.graph.nodes()),
                    "edges": list(self.kg_manager.graph.edges(data=True))
                }
            }

        except Exception as e:
            print(f"Error in mechanism path analysis: {str(e)}")
            return {
                "error": f"Failed to analyze mechanism paths: {str(e)}",
                "concept_paths": [],
                "hypothesis": {
                    "hypothesis": "Analysis failed",
                    "mechanisms": {"pathways": [], "interactions": [], "regulation": []},
                    "evidence": {"experimental": [], "computational": [], "clinical": []},
                    "predictions": [],
                    "novelty_scores": {"pathways": 0, "evidence": 0, "overall": 0},
                    "therapeutic_implications": {"drug_targets": [], "biomarkers": [], "treatment_strategies": []},
                    "future_directions": {"key_questions": [], "technical_needs": [], "validation_approaches": []}
                },
                "knowledge_graph": {"nodes": [], "edges": []}
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
                self.kg_manager.extract_subgraph(seed_path)
                if seed_path and "nodes" in seed_path
                else self.kg_manager.graph
            )

            validation_prompt = f"""
            Validate this scientific hypothesis using the knowledge graph evidence:
            Hypothesis: {hypothesis.get("hypothesis", "")}
            Graph Evidence: {json.dumps(list(relevant_subgraph.edges(data=True)), indent=2)}
            Novelty Score: {hypothesis.get("novelty_score", 0.5)}

            Leverage Claude's comprehensive analysis capabilities to consider:
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
                validation = json.loads(validation)

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