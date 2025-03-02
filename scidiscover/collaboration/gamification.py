"""
Gamification system for collaborative hypothesis building
"""
from dataclasses import dataclass
from typing import List, Dict, Optional
from datetime import datetime

@dataclass
class Contribution:
    """Scientific contribution with gamification elements"""
    id: str
    user_id: str
    hypothesis_id: str
    content: str
    evidence_score: float  # 0-1 score for evidence strength
    novelty_score: float   # 0-1 score for novelty
    timestamp: datetime
    points: int
    references: List[str]  # IDs of referenced papers/evidence
    
class GamificationManager:
    """Manages scoring and rewards for scientific contributions"""
    
    def __init__(self):
        self.contributions: Dict[str, Contribution] = {}
        self.user_scores: Dict[str, int] = {}
        
    def calculate_contribution_score(self, contribution: Contribution) -> int:
        """
        Calculate points for a scientific contribution
        
        Scoring factors:
        - Evidence strength (0-40 points)
        - Novelty (0-30 points)
        - References quality (0-20 points)
        - Community validation (0-10 points)
        """
        evidence_points = int(contribution.evidence_score * 40)
        novelty_points = int(contribution.novelty_score * 30)
        reference_points = min(len(contribution.references) * 5, 20)
        
        return evidence_points + novelty_points + reference_points
    
    def add_contribution(self, 
                        user_id: str,
                        hypothesis_id: str,
                        content: str,
                        evidence_score: float,
                        novelty_score: float,
                        references: List[str]) -> Contribution:
        """
        Add a new scientific contribution
        
        Returns the created contribution with calculated points
        """
        contribution = Contribution(
            id=f"c_{len(self.contributions)}",
            user_id=user_id,
            hypothesis_id=hypothesis_id,
            content=content,
            evidence_score=evidence_score,
            novelty_score=novelty_score,
            timestamp=datetime.now(),
            points=0,  # Will be calculated
            references=references
        )
        
        # Calculate points
        points = self.calculate_contribution_score(contribution)
        contribution.points = points
        
        # Update user score
        if user_id not in self.user_scores:
            self.user_scores[user_id] = 0
        self.user_scores[user_id] += points
        
        # Store contribution
        self.contributions[contribution.id] = contribution
        
        return contribution
    
    def get_user_achievements(self, user_id: str) -> Dict:
        """Get user's scientific achievements and stats"""
        user_contributions = [c for c in self.contributions.values() 
                            if c.user_id == user_id]
        
        return {
            "total_score": self.user_scores.get(user_id, 0),
            "contributions": len(user_contributions),
            "top_contribution": max([c.points for c in user_contributions], default=0),
            "expertise_level": self._calculate_expertise_level(
                self.user_scores.get(user_id, 0)
            )
        }
    
    def _calculate_expertise_level(self, score: int) -> str:
        """Calculate user's expertise level based on points"""
        if score < 100:
            return "Research Assistant"
        elif score < 500:
            return "Postdoc Researcher"
        elif score < 1000:
            return "Senior Scientist"
        elif score < 5000:
            return "Principal Investigator"
        else:
            return "Distinguished Researcher"
