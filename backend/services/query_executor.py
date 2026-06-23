from __future__ import annotations
import logging, os
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout
from typing import Any, Dict, List

logger = logging.getLogger("nyai.services.query_executor")

_RETRIEVER_POOL = ThreadPoolExecutor(max_workers=2, thread_name_prefix="retriever")
_RERANKER_POOL = ThreadPoolExecutor(max_workers=2, thread_name_prefix="reranker")

def run_hybrid_retrieval(expanded_queries: List[str], top_k: int = 10) -> Dict[str, Any]:
    hybrid_timeout = float(os.getenv("HYBRID_RETRIEVER_TIMEOUT_SECONDS", "12"))
    hybrid_enabled = os.getenv("HYBRID_RETRIEVER_ENABLED", "true").lower() not in {"0", "false", "no"}
    if not hybrid_enabled:
        return {"candidates": [], "sections_found": 0, "query_logs": []}
    try:
        from services.retriever import get_hybrid_retriever
        future = _RETRIEVER_POOL.submit(lambda: get_hybrid_retriever().hybrid_search(expanded_queries, top_k=top_k))
        return future.result(timeout=hybrid_timeout)
    except FutureTimeout:
        logger.warning("Hybrid retrieval timed out")
        return {"candidates": [], "sections_found": 0, "query_logs": []}
    except Exception as exc:
        logger.warning("Hybrid retrieval unavailable: %s", exc)
        return {"candidates": [], "sections_found": 0, "query_logs": []}

def run_reranker(query: str, candidate_records: List[Dict[str, Any]], top_k: int = 5) -> List[Dict[str, Any]]:
    reranker_timeout = float(os.getenv("RERANKER_TIMEOUT_SECONDS", "8"))
    reranker_enabled = os.getenv("RERANKER_ENABLED", "true").lower() not in {"0", "false", "no"}
    if not reranker_enabled or not candidate_records:
        return candidate_records[:top_k]
    try:
        from services.reranker import rerank_sections
        future = _RERANKER_POOL.submit(lambda: rerank_sections(query, candidate_records, top_k=top_k))
        return future.result(timeout=reranker_timeout)
    except FutureTimeout:
        logger.warning("Reranker timed out")
        return candidate_records[:top_k]
    except Exception as exc:
        logger.warning("Reranker unavailable: %s", exc)
        return candidate_records[:top_k]
