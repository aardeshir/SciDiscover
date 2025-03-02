"""
Knowledge Graph Reasoning Agent
Implements scientific discovery through graph-based concept exploration
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

        If novelty_score is low or include_established is true, include:
        - Well-validated mechanisms
        - Classical pathways
        - Foundational discoveries
        - Established experimental evidence

        Format your response as a JSON array of relationships with this structure:
        [
            {{
                "source": "concept1",
                "target": "concept2",
                "type": "mechanistic relationship type",
                "evidence": ["supporting evidence 1", "supporting evidence 2"],
                "novelty": float  # 0-1 score indicating how novel this relationship is
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

            Consider:
            1. Sequential progression through each path
            2. Mechanistic connections between concepts
            3. Supporting experimental evidence
            4. Potential regulatory interactions

            If novelty_score is high, emphasize:
            - Recently discovered mechanisms
            - Novel pathway interactions
            - Emerging therapeutic targets
            - Cutting-edge experimental approaches

            If novelty_score is low or include_established is true, include:
            - Well-validated mechanisms
            - Classical regulatory pathways
            - Established experimental evidence

            Format your response as a JSON object with this structure:
            {{
                "hypothesis": "detailed hypothesis statement",
                "mechanisms": {{
                    "pathways": ["key pathways identified"],
                    "interactions": ["mechanistic interactions"],
                    "regulation": ["regulatory mechanisms"]
                }},
                "evidence": ["supporting evidence"],
                "predictions": ["testable predictions"],
                "novelty_scores": {{
                    "pathways": float,  # Average novelty of pathways
                    "evidence": float,  # Average novelty of evidence
                    "overall": float    # Overall hypothesis novelty
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
                    "evidence": [],
                    "predictions": [],
                    "novelty_scores": {"pathways": 0, "evidence": 0, "overall": 0}
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

            Consider:
            1. Support from graph relationships
            2. Completeness of mechanistic explanation
            3. Alternative paths or mechanisms
            4. Potential gaps in evidence
            5. Balance between novelty and established knowledge

            Format your response as a JSON object with this structure:
            {{
                "validation": {{
                    "supported_claims": ["list of supported claims"],
                    "missing_evidence": ["gaps in evidence"],
                    "alternative_mechanisms": ["other possible mechanisms"],
                    "novelty_assessment": {{
                        "innovative_aspects": ["novel elements identified"],
                        "established_foundations": ["well-validated components"],
                        "score": float  # 0-1 novelty score
                    }}
                }},
                "confidence_score": float  # 0-1 score
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
                        "score": 0.0
                    }
                },
                "confidence_score": 0.0
            }