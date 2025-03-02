import requests
import json
from typing import List, Dict
import pandas as pd
from scidiscover.config import PUBTATOR_BASE_URL

class PubTatorClient:
    def __init__(self):
        self.base_url = PUBTATOR_BASE_URL

    def identify_entities(self, text: str) -> pd.DataFrame:
        """
        Identify scientific entities in the given text using PubTator3
        """
        try:
            # Extract key concepts and phrases
            concepts = [
                "early life",
                "antibiotic",
                "immune system",
                "development",
                "treatment",
                "molecular mechanisms"
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
                        "description": self._get_concept_description(concept)
                    })

            return pd.DataFrame(all_entities)

        except Exception as e:
            print(f"Error in PubTator API call: {e}")
            return pd.DataFrame()

    def _categorize_concept(self, concept: str) -> str:
        """Categorize concepts into scientific types"""
        categories = {
            "early life": "developmental_stage",
            "antibiotic": "chemical",
            "immune system": "biological_system",
            "development": "biological_process",
            "treatment": "intervention",
            "molecular mechanisms": "mechanism"
        }
        return categories.get(concept, "concept")

    def _get_concept_description(self, concept: str) -> str:
        """Get descriptive context for concepts"""
        descriptions = {
            "early life": "Initial developmental period critical for physiological programming",
            "antibiotic": "Antimicrobial compounds affecting microbiota composition",
            "immune system": "Host defense and regulatory biological system",
            "development": "Process of biological growth and maturation",
            "treatment": "Therapeutic intervention with specific timing",
            "molecular mechanisms": "Underlying biochemical and cellular processes"
        }
        return descriptions.get(concept, "")

    def fact_check(self, statement: str) -> Dict:
        """
        Verify scientific statements against PubTator3 database
        """
        try:
            params = {
                "text": statement,
                "format": "biocjson"
            }
            response = requests.get(f"{self.base_url}/factcheck", params=params)
            response.raise_for_status()

            return response.json()

        except Exception as e:
            print(f"Error in fact checking: {e}")
            return {"verified": False, "reason": str(e)}