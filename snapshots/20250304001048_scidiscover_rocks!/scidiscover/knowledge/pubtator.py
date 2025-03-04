import requests
import json
from typing import List, Dict, Union, Optional
import pandas as pd
from scidiscover.config import PUBTATOR_BASE_URL

class PubTatorClient:
    def __init__(self):
        self.base_url = PUBTATOR_BASE_URL
        # Expanded entity categories for more comprehensive biomedical entity recognition
        self.entity_categories = {
            "Gene": ["gene", "protein", "enzyme", "transcription factor"],
            "Disease": ["disease", "disorder", "syndrome", "condition", "pathology"],
            "Chemical": ["drug", "compound", "medication", "antibiotic", "small molecule"],
            "Species": ["organism", "bacteria", "virus", "microbe", "pathogen"],
            "Cellular": ["cell", "receptor", "pathway", "signaling", "organelle"],
            "Molecular": ["function", "activity", "binding", "catalysis", "interaction"],
            "Biological": ["process", "mechanism", "regulation", "development", "response"]
        }

    def identify_entities(self, text: str) -> pd.DataFrame:
        """
        Identify scientific entities in the given text using enhanced multi-source approach
        """
        try:
            # Start with PubTator-style entities
            base_entities = self._extract_base_entities(text)

            # Extract additional entities using specialized methods
            additional_entities = self._extract_advanced_entities(text)

            # Merge and deduplicate entities
            all_entities = self._merge_entities(base_entities, additional_entities)

            # Assign confidence scores
            self._assign_confidence_scores(all_entities, text)

            return pd.DataFrame(all_entities)

        except Exception as e:
            print(f"Error in entity identification: {e}")
            return pd.DataFrame()

    def _extract_base_entities(self, text: str) -> List[Dict]:
        """Extract core entities using base categorization"""
        # Simplified entity extraction for demo purposes
        concepts = [
            "early life",
            "antibiotic",
            "immune system",
            "development",
            "treatment",
            "molecular mechanisms",
            "microbiome",
            "dysbiosis",
            "inflammation",
            "cytokine",
            "T cell",
            "B cell",
            "macrophage",
            "epithelium",
            "barrier function"
        ]

        all_entities = []

        # Create concept nodes with better categorization
        for concept in concepts:
            if concept.lower() in text.lower():
                entity_type = self._categorize_concept(concept)
                all_entities.append({
                    "type": entity_type,
                    "text": concept,
                    "identifier": f"concept_{len(all_entities)}",
                    "source_phrase": text,
                    "description": self._get_concept_description(concept),
                    "source": "base"
                })

        return all_entities

    def _extract_advanced_entities(self, text: str) -> List[Dict]:
        """Extract advanced entities using more sophisticated methods"""
        # This would normally involve NER models or API calls
        # For demonstration, we'll use a rule-based approach

        advanced_entities = []

        # Additional specialized entity types to look for
        specialized_terms = {
            "toll-like receptor": "receptor",
            "NF-κB": "transcription_factor",
            "IL-6": "cytokine",
            "TNF-α": "cytokine",
            "intestinal permeability": "physiological_process", 
            "short-chain fatty acids": "metabolite",
            "Bacteroidetes": "bacterial_taxa",
            "Firmicutes": "bacterial_taxa",
            "Proteobacteria": "bacterial_taxa",
            "regulatory T cells": "immune_cell",
            "dendritic cells": "immune_cell",
            "mucus layer": "barrier_component",
            "antimicrobial peptides": "effector_molecule",
            "pattern recognition receptors": "sensor_molecule"
        }

        # Simple term detection
        for term, entity_type in specialized_terms.items():
            if term.lower() in text.lower():
                advanced_entities.append({
                    "type": entity_type,
                    "text": term,
                    "identifier": f"advanced_{len(advanced_entities)}",
                    "source_phrase": text,
                    "description": f"Advanced {entity_type} entity",
                    "source": "specialized"
                })

        return advanced_entities

    def _merge_entities(self, base_entities: List[Dict], 
                      additional_entities: List[Dict]) -> List[Dict]:
        """Merge entities from multiple sources and deduplicate"""
        merged = base_entities.copy()

        # Check for duplicates and merge
        for new_entity in additional_entities:
            duplicate = False
            for existing in merged:
                # Check if this is effectively the same entity
                if (new_entity["text"].lower() == existing["text"].lower() or
                    new_entity["text"].lower() in existing["text"].lower() or
                    existing["text"].lower() in new_entity["text"].lower()):

                    duplicate = True
                    # Update source to indicate multiple sources
                    if existing["source"] != "multiple":
                        existing["source"] = "multiple"

                    # Keep the more specific entity text
                    if len(new_entity["text"]) > len(existing["text"]):
                        existing["text"] = new_entity["text"]

                    # Merge descriptions if available
                    if "description" in new_entity and "description" in existing:
                        existing["description"] = f"{existing['description']}; {new_entity['description']}"

                    break

            # Add if not a duplicate
            if not duplicate:
                merged.append(new_entity)

        return merged

    def _assign_confidence_scores(self, entities: List[Dict], context: str) -> None:
        """Assign confidence scores to entities based on various factors"""
        for entity in entities:
            base_score = 0.7  # Default confidence

            # Adjust based on source
            if entity["source"] == "multiple":
                base_score += 0.2  # Multiple sources increases confidence
            elif entity["source"] == "specialized":
                base_score += 0.1  # Specialized detection has higher baseline

            # Adjust based on context relevance
            context_relevance = self._calculate_context_relevance(entity["text"], context)
            base_score += context_relevance * 0.1

            # Cap at 0.99
            entity["confidence"] = min(0.99, base_score)

    def _calculate_context_relevance(self, entity: str, context: str) -> float:
        """Calculate how relevant an entity is within the given context"""
        # Simple implementation - could be replaced with semantic similarity
        context_words = context.lower().split()
        entity_words = entity.lower().split()

        # Count occurrences of entity words in context
        occurrences = sum(1 for word in entity_words if word in context_words)

        # Normalize by entity length
        return min(1.0, occurrences / max(1, len(entity_words)))

    def _categorize_concept(self, concept: str) -> str:
        """Categorize concepts into scientific types with enhanced granularity"""
        categories = {
            "early life": "developmental_stage",
            "antibiotic": "chemical",
            "immune system": "biological_system",
            "development": "biological_process",
            "treatment": "intervention",
            "molecular mechanisms": "mechanism",
            "microbiome": "microbial_community",
            "dysbiosis": "pathological_state",
            "inflammation": "immune_response",
            "cytokine": "signaling_molecule",
            "T cell": "immune_cell",
            "B cell": "immune_cell",
            "macrophage": "immune_cell",
            "epithelium": "tissue_type",
            "barrier function": "physiological_process"
        }
        return categories.get(concept, "concept")

    def _get_concept_description(self, concept: str) -> str:
        """Get descriptive context for concepts with enhanced information"""
        descriptions = {
            "early life": "Initial developmental period critical for physiological programming with long-term health consequences",
            "antibiotic": "Antimicrobial compounds affecting microbiota composition and diversity with downstream immunological effects",
            "immune system": "Host defense and regulatory biological system comprising innate and adaptive components",
            "development": "Process of biological growth and maturation with critical windows of susceptibility",
            "treatment": "Therapeutic intervention with specific timing and dosage considerations",
            "molecular mechanisms": "Underlying biochemical and cellular processes mediating biological effects",
            "microbiome": "Complex community of microorganisms inhabiting a specific niche with diverse metabolic functions",
            "dysbiosis": "Microbial imbalance or maladaptation with pathological consequences for the host",
            "inflammation": "Protective response involving immune cells, blood vessels, and molecular mediators",
            "cytokine": "Small proteins crucial for cell signaling and immune regulation",
            "T cell": "Lymphocyte essential for cell-mediated immunity and cytokine production",
            "B cell": "Lymphocyte involved in antibody production and humoral immunity",
            "macrophage": "Phagocytic cell involved in innate immunity and tissue homeostasis",
            "epithelium": "Tissue forming barriers and specialized functional interfaces",
            "barrier function": "Physical and biochemical protection against environmental insults"
        }
        return descriptions.get(concept, "")

    def fact_check(self, statement: str) -> Dict:
        """
        Verify scientific statements against PubTator3 database with enhanced validation
        """
        try:
            # First attempt direct PubTator verification
            params = {
                "text": statement,
                "format": "biocjson"
            }
            response = requests.get(f"{self.base_url}/factcheck", params=params)
            response.raise_for_status()
            pubtator_result = response.json()

            # Enhance with confidence scoring
            verification_level = self._calculate_verification_confidence(pubtator_result, statement)

            return {
                "verified": verification_level > 0.5,
                "confidence": verification_level,
                "pubtator_match": pubtator_result.get("match", False),
                "supporting_evidence": self._extract_supporting_evidence(pubtator_result),
                "contradicting_evidence": self._extract_contradicting_evidence(pubtator_result)
            }

        except Exception as e:
            print(f"Error in fact checking: {e}")
            return {
                "verified": False, 
                "reason": str(e),
                "confidence": 0.0,
                "supporting_evidence": [],
                "contradicting_evidence": []
            }

    def _calculate_verification_confidence(self, pubtator_result: Dict, statement: str) -> float:
        """Calculate confidence level for verification result"""
        # Basic verification from PubTator
        if not pubtator_result.get("match", False):
            return 0.3  # Low confidence if no direct match

        # Extract entity matches
        entity_matches = pubtator_result.get("entity_matches", [])
        relationship_matches = pubtator_result.get("relationship_matches", [])

        # Calculate confidence based on matches
        base_confidence = 0.5

        # More entity matches increase confidence
        entity_boost = min(0.3, len(entity_matches) * 0.05)

        # Relationship matches strongly increase confidence
        relationship_boost = min(0.4, len(relationship_matches) * 0.1)

        # Calculate final confidence score
        verification_confidence = base_confidence + entity_boost + relationship_boost

        return min(0.99, verification_confidence)

    def _extract_supporting_evidence(self, pubtator_result: Dict) -> List[str]:
        """Extract supporting evidence from PubTator results"""
        supporting = []

        # Extract evidence from entity mentions
        entities = pubtator_result.get("entities", [])
        for entity in entities:
            if entity.get("confidence", 0) > 0.7:
                supporting.append(f"Entity '{entity.get('text', '')}' found with high confidence")

        # Extract relationship evidence
        relationships = pubtator_result.get("relationships", [])
        for rel in relationships:
            if rel.get("confidence", 0) > 0.7:
                supporting.append(f"Relationship between '{rel.get('source', '')}' and '{rel.get('target', '')}' confirmed")

        return supporting

    def _extract_contradicting_evidence(self, pubtator_result: Dict) -> List[str]:
        """Extract contradicting evidence from PubTator results"""
        contradicting = []

        # Extract evidence from entity mentions
        conflicts = pubtator_result.get("conflicts", [])
        for conflict in conflicts:
            contradicting.append(f"Contradiction: {conflict.get('description', 'unspecified conflict')}")

        return contradicting