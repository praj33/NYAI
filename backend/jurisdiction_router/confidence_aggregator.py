from typing import List, Dict, Any, Tuple

class ConfidenceAggregator:
    """
    Combines agent scores and selects the best output.
    Uses weighted scoring for deterministic and auditable results.
    """
    
    def __init__(self):
        # Weights for different factors in confidence calculation
        self.weights = {
            "agent_confidence": 0.4,
            "historical_performance": 0.3,
            "consistency": 0.2,
            "completeness": 0.1
        }
        
        # Historical performance cache (in a real system, this would be persistent)
        self.performance_history = {}
    
    def aggregate_confidence(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Aggregate confidence scores from multiple agent results.
        
        Args:
            results: List of agent result dictionaries
            
        Returns:
            Dictionary with best result and aggregated confidence
        """
        if not results:
            return {"selected_result": None, "confidence": 0.0, "selection_reason": "no_results"}
            
        if len(results) == 1:
            return {
                "selected_result": results[0],
                "confidence": results[0].get("confidence", 0.5),
                "selection_reason": "single_result"
            }
        
        # Calculate weighted scores for each result
        scored_results = []
        for result in results:
            weighted_score = self._calculate_weighted_score(result)
            scored_results.append((result, weighted_score))
        
        # Sort by weighted score (descending)
        scored_results.sort(key=lambda x: x[1], reverse=True)
        
        # Return the best result
        best_result, best_score = scored_results[0]
        
        return {
            "selected_result": best_result,
            "confidence": best_score,
            "selection_reason": f"best_weighted_score_among_{len(results)}",
            "all_scores": [score for _, score in scored_results]
        }
    
    def _calculate_weighted_score(self, result: Dict[str, Any]) -> float:
        """
        Calculate weighted confidence score for a single result.
        
        Args:
            result: Agent result dictionary
            
        Returns:
            Weighted confidence score (0.0 to 1.0)
        """
        # Base agent confidence
        agent_confidence = result.get("confidence", 0.5)
        
        # Historical performance of this agent/jurisdiction combination
        agent_key = f"{result.get('selected_agent', 'unknown')}_{result.get('jurisdiction', 'unknown')}"
        historical_performance = self.performance_history.get(agent_key, 0.5)
        
        # Consistency measure (placeholder - in a real system this would compare with other results)
        consistency = 0.5  # Default neutral value
        
        # Completeness measure (placeholder - in a real system this would check result completeness)
        completeness = 0.5  # Default neutral value
        
        # Calculate weighted score
        weighted_score = (
            self.weights["agent_confidence"] * agent_confidence +
            self.weights["historical_performance"] * historical_performance +
            self.weights["consistency"] * consistency +
            self.weights["completeness"] * completeness
        )
        
        # Ensure score is within bounds
        return max(0.0, min(1.0, weighted_score))
    
    def update_performance_history(self, agent_key: str, reward_score: float):
        """
        Update historical performance based on reward feedback.
        
        Args:
            agent_key: Identifier for agent/jurisdiction combination
            reward_score: Normalized reward score (0.0 to 1.0)
        """
        if agent_key not in self.performance_history:
            self.performance_history[agent_key] = reward_score
        else:
            # Simple moving average (in a real system, this might use exponential smoothing)
            current_performance = self.performance_history[agent_key]
            updated_performance = (current_performance + reward_score) / 2
            self.performance_history[agent_key] = updated_performance
    
    def adjust_weights(self, weight_updates: Dict[str, float]):
        """
        Adjust the weights used in confidence calculation.
        
        Args:
            weight_updates: Dictionary of weight adjustments
        """
        for key, value in weight_updates.items():
            if key in self.weights:
                self.weights[key] = max(0.0, min(1.0, value))  # Clamp between 0 and 1
                
        # Normalize weights to sum to 1.0
        total_weight = sum(self.weights.values())
        if total_weight > 0:
            for key in self.weights:
                self.weights[key] /= total_weight