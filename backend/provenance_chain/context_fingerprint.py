import hashlib
import json
from typing import Optional
from datetime import datetime

class ContextFingerprint:
    def __init__(self):
        pass

    def generate_fingerprint(self, query_text: str, user_id: Optional[str] = None,
                           jurisdiction: str = "global", timestamp: Optional[str] = None) -> str:
        """
        Generate a deterministic hash from request context.

        Args:
            query_text: The main query text
            user_id: Optional user identifier
            jurisdiction: Jurisdiction context
            timestamp: ISO timestamp, if not provided uses current time bucketed to hour

        Returns:
            SHA256 hash string of the context
        """
        if timestamp is None:
            # Bucket to hour for grouping similar requests
            now = datetime.utcnow()
            timestamp_bucket = now.strftime("%Y-%m-%dT%H:00:00Z")
        else:
            # Parse and bucket the provided timestamp
            dt = datetime.fromisoformat(timestamp.replace('Z', '+00:00'))
            timestamp_bucket = dt.strftime("%Y-%m-%dT%H:00:00Z")

        # Create deterministic context dict
        context = {
            "query_text": query_text.strip().lower(),  # Normalize
            "user_id": user_id,
            "jurisdiction": jurisdiction.lower(),
            "timestamp_bucket": timestamp_bucket
        }

        # Remove None values
        context = {k: v for k, v in context.items() if v is not None}

        # Create canonical JSON
        canonical_json = json.dumps(context, sort_keys=True, separators=(',', ':'))

        # Generate hash
        return hashlib.sha256(canonical_json.encode()).hexdigest()

# Global instance
fingerprint_generator = ContextFingerprint()