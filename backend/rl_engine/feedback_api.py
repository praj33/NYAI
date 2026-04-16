from typing import Dict, Any
import json
import time
import hashlib
import hmac
from rl_engine.reward_engine import RewardEngine
from jurisdiction_router.confidence_aggregator import ConfidenceAggregator
from provenance_chain.nonce_manager import nonce_manager

class FeedbackAPI:
    """
    API endpoint for receiving feedback JSON and processing rewards.
    Includes security: authentication, input validation, rate limiting.
    """

    def __init__(self, reward_engine: RewardEngine = None, confidence_aggregator: ConfidenceAggregator = None):
        self.reward_engine = reward_engine or RewardEngine()
        self.confidence_aggregator = confidence_aggregator or ConfidenceAggregator()

        # Security configuration
        self.api_key = "your-api-key-here"  # Should be from env
        self.rate_limit_window = 60  # seconds
        self.rate_limit_max_requests = 10  # per window
        self.rate_limit_cache = {}  # Simple in-memory cache

    def _authenticate_request(self, headers: Dict[str, str]) -> bool:
        """Authenticate request using API key."""
        auth_header = headers.get('Authorization', '')
        if not auth_header.startswith('Bearer '):
            return False

        provided_key = auth_header[7:]  # Remove 'Bearer '
        expected_key = self.api_key

        # Use constant-time comparison to prevent timing attacks
        return hmac.compare_digest(provided_key, expected_key)

    def _check_rate_limit(self, client_ip: str) -> bool:
        """Check if request is within rate limits."""
        current_time = time.time()

        if client_ip not in self.rate_limit_cache:
            self.rate_limit_cache[client_ip] = []

        # Clean old requests
        self.rate_limit_cache[client_ip] = [
            req_time for req_time in self.rate_limit_cache[client_ip]
            if current_time - req_time < self.rate_limit_window
        ]

        # Check if under limit
        if len(self.rate_limit_cache[client_ip]) >= self.rate_limit_max_requests:
            return False

        # Add current request
        self.rate_limit_cache[client_ip].append(current_time)
        return True

    def _validate_feedback_data(self, feedback_data: Dict[str, Any]) -> Dict[str, str]:
        """Validate feedback data comprehensively."""
        errors = {}

        # Required fields
        required_fields = ['trace_id', 'score', 'nonce']
        for field in required_fields:
            if field not in feedback_data:
                errors[field] = f"Missing required field: {field}"

        if errors:
            return errors

        # Validate trace_id format (should be UUID-like)
        trace_id = feedback_data['trace_id']
        if not isinstance(trace_id, str) or len(trace_id) < 10:
            errors['trace_id'] = "Invalid trace_id format"

        # Validate score
        score = feedback_data['score']
        if not isinstance(score, int) or score < 1 or score > 5:
            errors['score'] = "Score must be an integer between 1 and 5"

        # Validate nonce (anti-replay)
        nonce = feedback_data['nonce']
        if not isinstance(nonce, str) or not nonce_manager.validate_nonce(nonce):
            errors['nonce'] = "Invalid or expired nonce"

        # Optional comment validation
        comment = feedback_data.get('comment', '')
        if comment and (not isinstance(comment, str) or len(comment) > 1000):
            errors['comment'] = "Comment must be a string with max 1000 characters"

        return errors
    
    def receive_feedback(self, feedback_data: Dict[str, Any], headers: Dict[str, str] = None,
                        client_ip: str = "unknown") -> Dict[str, Any]:
        """
        Receive feedback and process reward assignment with security checks.

        Expected POST /rl/feedback format:
        {
            "trace_id": "...",
            "score": 1-5,
            "nonce": "...",
            "comment": "optional"
        }

        Headers should include:
        Authorization: Bearer <api_key>

        Returns:
        {
            "status": "recorded",
            "reward_assigned": "<numeric>",
            "updated_confidence": "<float>"
        }

        Args:
            feedback_data: Feedback data dictionary
            headers: Request headers for authentication
            client_ip: Client IP for rate limiting

        Returns:
            Response dictionary
        """
        headers = headers or {}

        # Security checks
        if not self._authenticate_request(headers):
            return {
                "status": "error",
                "message": "Authentication failed"
            }

        if not self._check_rate_limit(client_ip):
            return {
                "status": "error",
                "message": "Rate limit exceeded"
            }

        # Validate input data
        validation_errors = self._validate_feedback_data(feedback_data)
        if validation_errors:
            return {
                "status": "error",
                "message": "Validation failed",
                "errors": validation_errors
            }
        
        # In a real implementation, we would retrieve the original response using trace_id
        # For this implementation, we'll use a placeholder response
        placeholder_response = {
            "confidence": 0.5  # Default confidence
        }
        
        # Compute reward
        reward_score, reward_details = self.reward_engine.compute_reward(
            placeholder_response, feedback_data
        )
        
        # Update performance memory
        self.reward_engine.update_performance_memory(
            feedback_data["trace_id"], reward_score, reward_details
        )
        
        # Update confidence aggregator with performance data
        # In a real implementation, we'd have the specific agent key
        agent_key = f"agent_{feedback_data['trace_id'][:8]}"
        self.confidence_aggregator.update_performance_history(
            agent_key, (reward_score + 1) / 2  # Normalize from [-1,1] to [0,1]
        )
        
        # Return success response
        return {
            "status": "recorded",
            "reward_assigned": reward_score,
            "updated_confidence": (reward_score + 1) / 2,  # Normalized confidence
            "details": reward_details
        }
    
    def get_feedback_stats(self) -> Dict[str, Any]:
        """
        Get statistics about received feedback.
        
        Returns:
            Feedback statistics dictionary
        """
        memory = self.reward_engine.performance_memory
        total_feedback = sum(len(entries) for entries in memory.values())
        
        if total_feedback == 0:
            return {
                "total_feedback": 0,
                "average_reward": 0.0
            }
        
        total_reward = 0.0
        for entries in memory.values():
            for entry in entries:
                total_reward += entry["reward_score"]
        
        return {
            "total_feedback": total_feedback,
            "average_reward": total_reward / total_feedback
        }
    
    def export_feedback_data(self) -> str:
        """
        Export all feedback data as JSON string.
        
        Returns:
            JSON string of all feedback data
        """
        return json.dumps(self.reward_engine.performance_memory, indent=2)

# Example usage (not part of the API itself)
def create_feedback_endpoint():
    """
    Factory function to create a feedback API endpoint.
    """
    reward_engine = RewardEngine()
    confidence_aggregator = ConfidenceAggregator()
    return FeedbackAPI(reward_engine, confidence_aggregator)