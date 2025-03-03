"""
Elo-style rating system for scientific hypothesis evaluation.
Inspired by Google Coscientist's comparative hypothesis evaluation.
"""

import json
import math
import uuid
from typing import Dict, List, Tuple, Optional, Union
from datetime import datetime
import numpy as np

class HypothesisEloManager:
    """
    Manages Elo-style ratings for scientific hypotheses.
    Enables pairwise comparisons and tournament-style evaluation.
    """
    def __init__(self, llm_manager, initial_rating: int = 1500, k_factor: int = 32):
        """
        Initialize the Elo rating manager.
        
        Args:
            llm_manager: LLM interface for hypothesis evaluation
            initial_rating: Starting Elo rating for new hypotheses
            k_factor: K-factor for Elo rating adjustments (higher = more volatile)
        """
        self.llm_manager = llm_manager
        self.initial_rating = initial_rating
        self.k_factor = k_factor
        self.ratings = {}  # Maps hypothesis ID to current rating
        self.hypothesis_store = {}  # Maps hypothesis ID to content
        self.match_history = []  # Records of all comparisons
        
    def register_hypothesis(self, hypothesis: Dict, hypothesis_id: str = None) -> str:
        """
        Register a new hypothesis and assign initial rating.
        
        Args:
            hypothesis: The hypothesis content
            hypothesis_id: Optional custom ID, generated if not provided
            
        Returns:
            The hypothesis ID
        """
        if hypothesis_id is None:
            hypothesis_id = str(uuid.uuid4())
            
        # Only register if not already present
        if hypothesis_id not in self.ratings:
            self.ratings[hypothesis_id] = self.initial_rating
            self.hypothesis_store[hypothesis_id] = hypothesis
            
        return hypothesis_id
    
    def compare_hypotheses(self, 
                          hypothesis_a: Dict, 
                          hypothesis_b: Dict,
                          query: str,
                          update_ratings: bool = True) -> Dict:
        """
        Compare two hypotheses and update their Elo ratings.
        
        Args:
            hypothesis_a: First hypothesis
            hypothesis_b: Second hypothesis
            query: The original scientific query
            update_ratings: Whether to update ratings after comparison
            
        Returns:
            Comparison results including winner and new ratings
        """
        # Register hypotheses if new
        id_a = self.register_hypothesis(hypothesis_a)
        id_b = self.register_hypothesis(hypothesis_b)
        
        # Get current ratings
        rating_a = self.ratings[id_a]
        rating_b = self.ratings[id_b]
        
        # Compare hypotheses using LLM
        outcome = self._evaluate_comparison(hypothesis_a, hypothesis_b, query)
        outcome_score = outcome["outcome"]  # 1.0 = A wins, 0.5 = draw, 0.0 = B wins
        
        # Calculate expected scores
        expected_a = self._expected_score(rating_a, rating_b)
        expected_b = 1.0 - expected_a
        
        # Update ratings if requested
        new_rating_a = rating_a
        new_rating_b = rating_b
        
        if update_ratings:
            new_rating_a = self._updated_rating(rating_a, outcome_score, expected_a)
            new_rating_b = self._updated_rating(rating_b, 1.0 - outcome_score, expected_b)
            
            # Update stored ratings
            self.ratings[id_a] = new_rating_a
            self.ratings[id_b] = new_rating_b
        
        # Record match in history
        match_record = {
            "timestamp": datetime.now().isoformat(),
            "hypothesis_a": id_a,
            "hypothesis_b": id_b,
            "query": query,
            "rating_a_before": rating_a,
            "rating_b_before": rating_b,
            "outcome": outcome_score,
            "rating_a_after": new_rating_a,
            "rating_b_after": new_rating_b,
            "expected_a": expected_a,
            "expected_b": expected_b,
            "reasoning": outcome.get("reasoning", ""),
            "comparative_strengths": outcome.get("comparative_strengths", []),
            "comparative_weaknesses": outcome.get("comparative_weaknesses", [])
        }
        
        self.match_history.append(match_record)
        
        # Return match results
        return {
            "winner_id": id_a if outcome_score > 0.5 else (None if outcome_score == 0.5 else id_b),
            "outcome_score": outcome_score,
            "hypothesis_a": {
                "id": id_a,
                "old_rating": rating_a,
                "new_rating": new_rating_a
            },
            "hypothesis_b": {
                "id": id_b,
                "old_rating": rating_b,
                "new_rating": new_rating_b
            },
            "comparative_analysis": outcome
        }
    
    def _evaluate_comparison(self, hypothesis_a: Dict, hypothesis_b: Dict, query: str) -> Dict:
        """
        Use LLM to compare two hypotheses and determine which is better.
        
        Args:
            hypothesis_a: First hypothesis
            hypothesis_b: Second hypothesis
            query: The original scientific query
            
        Returns:
            Comparison outcome (1.0 = A wins, 0.5 = draw, 0.0 = B wins)
        """
        comparison_prompt = f"""
        Compare these two scientific hypotheses addressing the query: "{query}"
        
        Hypothesis A:
        {json.dumps(hypothesis_a, indent=2)}
        
        Hypothesis B:
        {json.dumps(hypothesis_b, indent=2)}
        
        Evaluate which hypothesis provides a better scientific explanation according to:
        1. Scientific rigor and accuracy
        2. Mechanistic detail and clarity
        3. Evidence support and citations
        4. Internal consistency and logic
        5. Explanatory power and scope
        
        Return a JSON object with:
        - "outcome": a float between 0 and 1, where:
          * 1.0 means Hypothesis A is clearly superior
          * 0.0 means Hypothesis B is clearly superior  
          * 0.5 means they are equally strong
        - "reasoning": explanation for your decision
        - "comparative_strengths": list of strengths of the winner compared to the other
        - "comparative_weaknesses": list of weaknesses of the loser compared to the other
        - "confidence": your confidence in this judgment (0-1)
        
        Focus on objective scientific merit, not subjective preference.
        """
        
        response = self.llm_manager.generate_response(comparison_prompt, model="anthropic", response_format="json")
        
        # Handle string or dict response formats
        if isinstance(response, str):
            try:
                parsed_response = json.loads(response)
                return parsed_response
            except json.JSONDecodeError:
                # Default to draw if parsing fails
                return {
                    "outcome": 0.5,
                    "reasoning": "Unable to parse response, defaulting to draw.",
                    "comparative_strengths": [],
                    "comparative_weaknesses": [],
                    "confidence": 0.5
                }
        
        return response
    
    def _expected_score(self, rating_a: float, rating_b: float) -> float:
        """
        Calculate expected score for player A using Elo formula.
        
        Args:
            rating_a: Rating of first hypothesis
            rating_b: Rating of second hypothesis
            
        Returns:
            Expected score for hypothesis A (between 0 and 1)
        """
        return 1.0 / (1.0 + 10.0 ** ((rating_b - rating_a) / 400.0))
    
    def _updated_rating(self, old_rating: float, actual_score: float, expected_score: float) -> float:
        """
        Calculate updated Elo rating.
        
        Args:
            old_rating: Previous rating
            actual_score: Actual outcome (1=win, 0.5=draw, 0=loss)
            expected_score: Expected outcome based on ratings
            
        Returns:
            New rating
        """
        return old_rating + self.k_factor * (actual_score - expected_score)
    
    def run_tournament(self, hypotheses: List[Dict], query: str, rounds: int = 2) -> Dict:
        """
        Run a tournament between multiple hypotheses to find the strongest.
        
        Args:
            hypotheses: List of hypotheses to compare
            query: The original scientific query
            rounds: Number of tournament rounds
            
        Returns:
            Tournament results including rankings
        """
        if len(hypotheses) < 2:
            return {"error": "Need at least 2 hypotheses for a tournament"}
        
        # Register all hypotheses
        hypothesis_ids = []
        for hyp in hypotheses:
            hyp_id = self.register_hypothesis(hyp)
            hypothesis_ids.append(hyp_id)
        
        # Run pairwise comparisons for specified rounds
        for round_num in range(1, rounds + 1):
            print(f"Tournament Round {round_num}")
            
            # Generate pairings for this round
            if round_num == 1:
                # First round: random pairings
                np.random.shuffle(hypothesis_ids)
                pairings = [(hypothesis_ids[i], hypothesis_ids[i+1]) 
                           for i in range(0, len(hypothesis_ids)-1, 2)]
                
                # Handle odd number of hypotheses
                if len(hypothesis_ids) % 2 == 1:
                    pairings.append((hypothesis_ids[-1], hypothesis_ids[0]))
            else:
                # Later rounds: match by rating (highest vs next highest)
                sorted_ids = sorted(hypothesis_ids, 
                                  key=lambda id: self.ratings[id], 
                                  reverse=True)
                
                pairings = [(sorted_ids[i], sorted_ids[i+1]) 
                           for i in range(0, len(sorted_ids)-1, 2)]
                
                # Handle odd number
                if len(sorted_ids) % 2 == 1:
                    pairings.append((sorted_ids[-1], sorted_ids[0]))
            
            # Run the matches for this round
            round_results = []
            for id_a, id_b in pairings:
                hyp_a = self.hypothesis_store[id_a]
                hyp_b = self.hypothesis_store[id_b]
                
                result = self.compare_hypotheses(hyp_a, hyp_b, query)
                round_results.append(result)
                
                print(f"Match: {id_a[:8]} vs {id_b[:8]} - Winner: {result['winner_id'][:8] if result['winner_id'] else 'Draw'}")
        
        # Return final rankings
        ranked_hypotheses = sorted(hypothesis_ids, 
                                 key=lambda id: self.ratings[id], 
                                 reverse=True)
        
        rankings = [
            {
                "rank": i+1,
                "hypothesis_id": h_id,
                "rating": self.ratings[h_id],
                "content": self.hypothesis_store[h_id]
            }
            for i, h_id in enumerate(ranked_hypotheses)
        ]
        
        return {
            "rankings": rankings,
            "match_history": self.match_history,
            "best_hypothesis": self.hypothesis_store[ranked_hypotheses[0]],
            "best_hypothesis_id": ranked_hypotheses[0],
            "best_hypothesis_rating": self.ratings[ranked_hypotheses[0]]
        }
    
    def get_hypothesis_rating(self, hypothesis_id: str) -> Optional[float]:
        """Get current rating for a hypothesis"""
        return self.ratings.get(hypothesis_id)
    
    def get_match_history(self, hypothesis_id: Optional[str] = None) -> List[Dict]:
        """Get match history, optionally filtered by hypothesis ID"""
        if hypothesis_id is None:
            return self.match_history
        
        return [
            match for match in self.match_history 
            if match["hypothesis_a"] == hypothesis_id or match["hypothesis_b"] == hypothesis_id
        ]
    
    def get_rating_history(self, hypothesis_id: str) -> List[Tuple[str, float]]:
        """Get rating history for a specific hypothesis"""
        history = []
        
        for match in self.match_history:
            if match["hypothesis_a"] == hypothesis_id:
                history.append((match["timestamp"], match["rating_a_after"]))
            elif match["hypothesis_b"] == hypothesis_id:
                history.append((match["timestamp"], match["rating_b_after"]))
                
        # Sort by timestamp
        history.sort(key=lambda x: x[0])
        return history
    
    def get_leaderboard(self, top_n: int = 10) -> List[Dict]:
        """Get current hypothesis leaderboard"""
        hypothesis_ids = list(self.ratings.keys())
        top_hypotheses = sorted(hypothesis_ids, 
                              key=lambda id: self.ratings[id], 
                              reverse=True)[:top_n]
        
        return [
            {
                "rank": i+1,
                "hypothesis_id": h_id,
                "rating": self.ratings[h_id]
            }
            for i, h_id in enumerate(top_hypotheses)
        ]
