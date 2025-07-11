import json
import os
from typing import List, Tuple

class ScoreManager:
    """Manages player scores and leaderboard"""
    def __init__(self, filename: str = "scores.json"):
        self.filename = filename
        self.scores = self._load_scores()
    
    def _load_scores(self) -> List[Tuple[str, int]]:
        """Load scores from file"""
        try:
            if os.path.exists(self.filename):
                with open(self.filename, 'r') as f:
                    data = json.load(f)
                    return [(item['name'], item['score']) for item in data]
            return []
        except (json.JSONDecodeError, KeyError):
            return []
    
    def _save_scores(self):
        """Save scores to file"""
        try:
            data = [{'name': name, 'score': score} for name, score in self.scores]
            with open(self.filename, 'w') as f:
                json.dump(data, f, indent=2)
        except Exception as e:
            print(f"Error saving scores: {e}")
    
    def add_score(self, name: str, score: int):
        """Add a new score to the leaderboard"""
        self.scores.append((name, score))
        self.scores.sort(key=lambda x: x[1], reverse=True)  # Sort by score descending
        self.scores = self.scores[:50]  # Keep top 50 scores
        self._save_scores()
    
    def get_top_scores(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get top scores"""
        return self.scores[:limit]
    
    def get_player_best(self, name: str) -> int:
        """Get player's best score"""
        player_scores = [score for n, score in self.scores if n == name]
        return max(player_scores) if player_scores else 0
    
    def clear_scores(self):
        """Clear all scores"""
        self.scores = []
        self._save_scores()
