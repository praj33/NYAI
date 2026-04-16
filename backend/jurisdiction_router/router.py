import re
from typing import Tuple, Dict, Any

class JurisdictionRouter:
    """
    Maps queries to jurisdictions using pattern matching and heuristics.
    Rules are extendable without code rewriting.
    """
    
    def __init__(self):
        # Configurable jurisdiction patterns - can be loaded from external config
        self.jurisdiction_patterns = {
            "IN": [
                r"\b(india|indian|delhi|mumbai|kolkata|chennai|bangalore|bengaluru)\b",
                r"\b(bharat|hindustan)\b",
                r"\b(indian parliament|supreme court of india|indian constitution)\b"
            ],
            "UK": [
                r"\b(united kingdom|britain|british|london|parliament uk|uk parliament)\b",
                r"\b(england|scotland|wales)\b",
                r"\b(house of commons|house of lords)\b"
            ],
            "UAE": [
                r"\b(uae|united arab emirates|dubai|abu dhabi|sharjah)\b",
                r"\b(emirate|emirati)\b",
                r"\b(federal national council)\b"
            ]
        }
        
        # Default jurisdiction weights
        self.jurisdiction_weights = {
            "IN": 1.0,
            "UK": 1.0,
            "UAE": 1.0
        }
    
    def route_query(self, query: str, metadata: Dict[Any, Any] = None) -> Tuple[str, float]:
        """
        Determine jurisdiction for a query based on pattern matching.
        
        Args:
            query: Text query to analyze
            metadata: Optional metadata dict
            
        Returns:
            Tuple of (jurisdiction_label, confidence_score)
        """
        # Initialize scores
        scores = {jurisdiction: 0.0 for jurisdiction in self.jurisdiction_patterns.keys()}
        
        # Convert query to lowercase for matching
        query_lower = query.lower()
        
        # Score each jurisdiction based on pattern matches
        for jurisdiction, patterns in self.jurisdiction_patterns.items():
            for pattern in patterns:
                if re.search(pattern, query_lower):
                    scores[jurisdiction] += self.jurisdiction_weights[jurisdiction]
        
        # Find the highest scoring jurisdiction
        best_jurisdiction = max(scores, key=scores.get)
        max_score = scores[best_jurisdiction]
        
        # Normalize confidence score (simple approach)
        total_score = sum(scores.values())
        confidence = max_score / total_score if total_score > 0 else 0.0
        
        # If no patterns matched, return default jurisdiction with low confidence
        if max_score == 0:
            return "IN", 0.1  # Default to India with low confidence
            
        return best_jurisdiction, confidence
    
    def add_jurisdiction_pattern(self, jurisdiction: str, pattern: str, weight: float = 1.0):
        """
        Add a new jurisdiction pattern for extensibility.
        
        Args:
            jurisdiction: Jurisdiction code (e.g., "IN", "UK", "UAE")
            pattern: Regex pattern to match
            weight: Weight for this pattern in scoring
        """
        if jurisdiction not in self.jurisdiction_patterns:
            self.jurisdiction_patterns[jurisdiction] = []
            self.jurisdiction_weights[jurisdiction] = weight
        else:
            self.jurisdiction_weights[jurisdiction] = weight
            
        self.jurisdiction_patterns[jurisdiction].append(pattern)