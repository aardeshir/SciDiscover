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
            params = {
                "text": text,
                "concepts": "gene,disease,chemical"
            }
            response = requests.get(self.base_url, params=params)
            response.raise_for_status()

            data = response.json()
            entities = []

            for annotation in data.get("annotations", []):
                entities.append({
                    "type": annotation["infons"]["type"],
                    "text": annotation["text"],
                    "identifier": annotation["infons"].get("identifier", "")
                })

            return pd.DataFrame(entities)

        except Exception as e:
            print(f"Error in PubTator API call: {e}")
            return pd.DataFrame()

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