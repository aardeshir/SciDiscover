import pandas as pd
from typing import Dict, List, Any
import json

class OutputFormatter:
    @staticmethod
    def format_hypothesis(hypothesis: Dict) -> str:
        """
        Format hypothesis output for display
        """
        formatted = f"""
        ## Hypothesis
        {hypothesis['hypothesis']}
        
        ### Supporting Concepts
        {', '.join(hypothesis['supporting_concepts'])}
        
        ### Predictions
        {''.join([f'- {p}\n' for p in hypothesis['predictions']])}
        
        ### Research Directions
        {''.join([f'- {r}\n' for r in hypothesis['research_directions']])}
        """
        return formatted
        
    @staticmethod
    def format_concept_network(graph: Dict) -> Dict:
        """
        Format network data for visualization
        """
        return {
            "nodes": [{"id": node, "label": node} for node in graph["nodes"]],
            "edges": [{"source": edge[0], "target": edge[1]} for edge in graph["edges"]]
        }
        
    @staticmethod
    def format_entities(entities: pd.DataFrame) -> List[Dict]:
        """
        Format entity data for display
        """
        return entities.to_dict('records')
