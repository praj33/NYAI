from typing import Dict, Any, List, Tuple
import asyncio
from jurisdiction_router.resolver_pipeline import ResolverPipeline

class FallbackManager:
    """
    Manages fallback processing when confidence is low.
    Automatically escalates to alternate jurisdictions if needed.
    """
    
    def __init__(self, resolver_pipeline: ResolverPipeline, confidence_threshold: float = 0.7):
        self.resolver_pipeline = resolver_pipeline
        self.confidence_threshold = confidence_threshold
        
        # Fallback jurisdiction priorities (ordered list)
        self.fallback_priorities = {
            "IN": ["UK", "UAE"],
            "UK": ["IN", "UAE"],
            "UAE": ["IN", "UK"]
        }
        
        # Maximum number of fallback attempts
        self.max_fallback_attempts = 2
    
    async def process_with_fallback(self, initial_jurisdiction: str, query: str, trace_id: str = None) -> Dict[str, Any]:
        """
        Process query with fallback mechanism if confidence is low.
        
        Args:
            initial_jurisdiction: Primary jurisdiction to try
            query: Query to process
            trace_id: Trace ID for tracking
            
        Returns:
            Final result with processing path
        """
        # Try primary jurisdiction
        primary_result = await self.resolver_pipeline.resolve_and_dispatch(
            initial_jurisdiction, query, trace_id
        )
        
        # Check if confidence is sufficient
        if primary_result["confidence"] >= self.confidence_threshold:
            primary_result["processing_path"] = [initial_jurisdiction]
            primary_result["fallback_used"] = False
            return primary_result
        
        # Confidence is low, try fallback jurisdictions
        fallback_results = [primary_result]
        processing_path = [initial_jurisdiction]
        
        # Get fallback jurisdictions for the primary one
        fallback_list = self.fallback_priorities.get(initial_jurisdiction, [])
        
        # Try up to max_fallback_attempts
        for i, fallback_jurisdiction in enumerate(fallback_list[:self.max_fallback_attempts]):
            fallback_result = await self.resolver_pipeline.resolve_and_dispatch(
                fallback_jurisdiction, query, trace_id
            )
            
            fallback_results.append(fallback_result)
            processing_path.append(fallback_jurisdiction)
            
            # If this fallback has high enough confidence, use it
            if fallback_result["confidence"] >= self.confidence_threshold:
                fallback_result["processing_path"] = processing_path
                fallback_result["fallback_used"] = True
                fallback_result["fallback_level"] = i + 1
                return fallback_result
        
        # If no fallback met the threshold, return the best result
        best_result = self._select_best_result(fallback_results)
        best_result["processing_path"] = processing_path
        best_result["fallback_used"] = True
        best_result["fallback_level"] = len(processing_path) - 1
        best_result["note"] = "No result met confidence threshold, returning best available"
        
        return best_result
    
    def _select_best_result(self, results: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Select the best result from a list based on confidence.
        
        Args:
            results: List of result dictionaries
            
        Returns:
            Best result dictionary
        """
        if not results:
            return {}
            
        # Sort by confidence (descending)
        sorted_results = sorted(results, key=lambda x: x.get("confidence", 0.0), reverse=True)
        return sorted_results[0]
    
    def update_confidence_threshold(self, new_threshold: float):
        """
        Update the confidence threshold for fallback activation.
        
        Args:
            new_threshold: New confidence threshold (0.0 to 1.0)
        """
        self.confidence_threshold = max(0.0, min(1.0, new_threshold))
    
    def update_fallback_priorities(self, jurisdiction: str, fallback_list: List[str]):
        """
        Update fallback priorities for a jurisdiction.
        
        Args:
            jurisdiction: Jurisdiction to update
            fallback_list: Ordered list of fallback jurisdictions
        """
        self.fallback_priorities[jurisdiction] = fallback_list