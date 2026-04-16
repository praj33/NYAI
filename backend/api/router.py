import sys
import os
current_dir = os.path.dirname(os.path.abspath(__file__))
project_root = os.path.dirname(current_dir)
if project_root not in sys.path:
    sys.path.append(project_root)
if os.getcwd() not in sys.path:
    sys.path.append(os.getcwd())

from fastapi import APIRouter, HTTPException, Query
from pydantic import BaseModel
from typing import Dict, Any, List, Optional
import uuid
import threading
from collections import OrderedDict
from datetime import datetime
from concurrent.futures import ThreadPoolExecutor, TimeoutError as FutureTimeout

# Import enhanced components
from clean_legal_advisor import EnhancedLegalAdvisor, LegalQuery

# Import jurisdiction detector
from core.jurisdiction.detector import JurisdictionDetector

# Import case law components
from core.caselaw.loader import CaseLawLoader
from core.caselaw.retriever import CaseLawRetriever

# Import original schemas
from api.schemas import (
    QueryRequest, MultiJurisdictionRequest, ExplainReasoningRequest,
    FeedbackRequest, NyayaResponse, MultiJurisdictionResponse,
    ExplainReasoningResponse, FeedbackResponse, TraceResponse,
    StatuteSchema, ConfidenceSchema, CaseLawSchema
)

# Import response enricher
from core.response.enricher import enrich_response
from services.explainer import generate_explanation_payload

# Import enforcement engine
from enforcement_engine.engine import SovereignEnforcementEngine
from enforcement_engine.decision_model import EnforcementSignal
from services.query_cleaner import clean_query
from services.query_understanding import analyze_query
from services.query_expander import expand_query
from services.retriever import get_hybrid_retriever
from services.reranker import rerank_sections
from services.legal_reasoner import apply_reasoning_rules
import logging

router = APIRouter(prefix="/nyaya", tags=["nyaya"])
logger = logging.getLogger(__name__)

# Initialize the enhanced legal advisor with error handling
try:
    advisor = EnhancedLegalAdvisor()
    jurisdiction_detector = JurisdictionDetector()
    enforcement_engine = SovereignEnforcementEngine()
    
    # Initialize case law system
    case_loader = CaseLawLoader()
    cases = case_loader.load_all()
    case_retriever = CaseLawRetriever(cases)
    print(f"Case law system initialized: {len(cases)} cases loaded")
    print("Jurisdiction detector initialized")
    print("Enforcement engine initialized")
except Exception as e:
    print(f"Error initializing components: {e}")
    advisor = None
    jurisdiction_detector = None
    case_retriever = None
    enforcement_engine = None

# ─── Response Cache (thread-safe LRU for trace_id lookups) ───
class ResponseCache:
    """Thread-safe LRU cache for query responses keyed by trace_id."""
    def __init__(self, max_size=500):
        self.cache = OrderedDict()
        self.max_size = max_size
        self.lock = threading.Lock()

    def set(self, trace_id: str, response: dict):
        with self.lock:
            self.cache[trace_id] = response
            if len(self.cache) > self.max_size:
                self.cache.popitem(last=False)

    def get(self, trace_id: str):
        with self.lock:
            return self.cache.get(trace_id)

response_cache = ResponseCache()

# ─── Pydantic models for new endpoints ───
class RLSignalRequest(BaseModel):
    trace_id: str
    signal_type: str = "feedback"
    user_feedback: Optional[str] = "neutral"
    outcome_tag: Optional[str] = "pending"


@router.post("/query", response_model=NyayaResponse)
async def query_legal(request: QueryRequest):
    """Execute a single-jurisdiction legal query with sovereign enforcement."""
    try:
        cleaned_query = clean_query(request.query)
        understanding = analyze_query(cleaned_query)
        understanding_domain = understanding.get("domain") if isinstance(understanding, dict) else None
        if not isinstance(understanding_domain, str) or not understanding_domain.strip():
            understanding_domain = "civil"
        domain_hint_value = understanding_domain
        if not domain_hint_value and request.domain_hint:
            domain_hint_value = request.domain_hint.value
        expanded_queries = expand_query(cleaned_query, understanding_domain)
        hybrid_result = {"candidates": [], "sections_found": 0, "query_logs": []}
        candidate_records = []

        hybrid_enabled = os.getenv("HYBRID_RETRIEVER_ENABLED", "true").lower() not in {"0", "false", "no"}
        hybrid_timeout = float(os.getenv("HYBRID_RETRIEVER_TIMEOUT_SECONDS", "12"))
        if hybrid_enabled:
            executor = ThreadPoolExecutor(max_workers=1)
            try:
                future = executor.submit(
                    lambda: get_hybrid_retriever().hybrid_search(expanded_queries, top_k=10)
                )
                hybrid_result = future.result(timeout=hybrid_timeout)
            except FutureTimeout:
                logger.warning("Hybrid retrieval timed out after %ss", hybrid_timeout)
            except Exception as exc:
                logger.warning("Hybrid retrieval unavailable: %s", exc)
            finally:
                executor.shutdown(wait=False, cancel_futures=True)
        candidate_records = hybrid_result.get("candidate_records") or hybrid_result.get("candidates") or []

        reranker_enabled = os.getenv("RERANKER_ENABLED", "true").lower() not in {"0", "false", "no"}
        reranker_timeout = float(os.getenv("RERANKER_TIMEOUT_SECONDS", "8"))
        if reranker_enabled and candidate_records:
            executor = ThreadPoolExecutor(max_workers=1)
            try:
                future = executor.submit(
                    lambda: rerank_sections(cleaned_query, candidate_records, top_k=5)
                )
                top_sections = future.result(timeout=reranker_timeout)
            except FutureTimeout:
                logger.warning("Reranker timed out after %ss", reranker_timeout)
                top_sections = candidate_records[:5]
            except Exception as exc:
                logger.warning("Reranker unavailable: %s", exc)
                top_sections = candidate_records[:5]
            finally:
                executor.shutdown(wait=False, cancel_futures=True)
        else:
            top_sections = candidate_records[:5]
        final_sections = apply_reasoning_rules(cleaned_query, understanding_domain, top_sections)
        reasoning_added = sum(
            1 for item in final_sections if item.get("source") == "reasoning_engine"
        )
        top_statutes = [
            {
                "act": item.get("act"),
                "year": item.get("year"),
                "section": item.get("section"),
                "title": item.get("title"),
                "source": item.get("source"),
            }
            for item in final_sections
        ]
        hybrid_result_public = {
            key: value for key, value in hybrid_result.items() if key != "candidate_records"
        }
        logger.info('original_query="%s" cleaned_query="%s"', request.query, cleaned_query)
        logger.info("expanded_queries=%s", expanded_queries)
        logger.info(
            "candidates_found=%s reranked_top=%s reasoning_added_sections=%s",
            len(candidate_records),
            len(top_sections),
            reasoning_added,
        )
        if understanding.get("source") == "local_fallback":
            logger.warning("LLM unavailable — using local fallback classifier.")

        # Check if advisor is initialized
        if advisor is None or jurisdiction_detector is None:
            raise HTTPException(
                status_code=500,
                detail={
                    "error_code": "ADVISOR_NOT_INITIALIZED",
                    "message": "Legal advisor failed to initialize. Check server logs.",
                    "trace_id": str(uuid.uuid4())
                }
            )
        
        # Detect jurisdiction from query
        jurisdiction_hint_str = request.jurisdiction_hint.value if request.jurisdiction_hint else None
        jurisdiction_result = jurisdiction_detector.detect(
            query=cleaned_query,
            user_hint=jurisdiction_hint_str
        )
        
        # DO NOT BYPASS EnhancedLegalAdvisor
        # Get legal advice using the enhanced advisor - SINGLE SOURCE OF TRUTH
        legal_query = LegalQuery(
            query_text=cleaned_query,
            jurisdiction_hint=request.jurisdiction_hint,
            domain_hint=domain_hint_value
        )
        advice = advisor.provide_legal_advice(legal_query)
        
        # Prefer deterministic pipeline statutes; fallback to advisor if empty
        statute_records = final_sections or []
        statute_source = "reasoning_pipeline"
        if not statute_records:
            statute_records = advice.statutes or []
            statute_source = "advisor_fallback"

        statutes = []
        seen_statutes = set()
        for statute in statute_records:
            act = str(statute.get("act", "")).strip()
            section = str(statute.get("section", "")).strip()
            title = str(statute.get("title", "")).strip()
            if not act or not section:
                continue
            year_raw = statute.get("year")
            try:
                year = int(year_raw) if year_raw is not None else 0
            except (TypeError, ValueError):
                year = 0
            key = (act.lower(), section.lower(), year)
            if key in seen_statutes:
                continue
            seen_statutes.add(key)
            statute_schema = StatuteSchema(
                act=act,
                year=year,
                section=section,
                title=title
            )
            statutes.append(statute_schema)

        sections_found = len(statutes)
        top_statutes = []
        seen_top = set()
        for item in statute_records:
            act = str(item.get("act", "")).strip()
            section = str(item.get("section", "")).strip()
            title = str(item.get("title", "")).strip()
            if not act or not section:
                continue
            year_raw = item.get("year")
            try:
                year = int(year_raw) if year_raw is not None else 0
            except (TypeError, ValueError):
                year = 0
            key = (act.lower(), section.lower(), year)
            if key in seen_top:
                continue
            seen_top.add(key)
            top_statutes.append(
                {
                    "act": act,
                    "year": year,
                    "section": section,
                    "title": title,
                    "source": item.get("source") or statute_source,
                }
            )
        
        # Retrieve relevant case laws
        case_laws = []
        if case_retriever:
            relevant_cases = case_retriever.retrieve(
                query=cleaned_query,
                domain=advice.domain,
                jurisdiction=advice.jurisdiction,
                top_k=3
            )
            case_laws = [
                CaseLawSchema(
                    title=case.title,
                    court=case.court,
                    year=case.year,
                    principle=case.principle
                )
                for case in relevant_cases
            ]
        
        # Build qualified legal analysis
        legal_analysis = _build_qualified_analysis(
            cleaned_query,
            statutes,
            advice.jurisdiction
        )
        
        # Calculate structured confidence
        confidence = _calculate_structured_confidence(
            sections_found,
            advice.confidence_score,
            advice.domain,
            cleaned_query
        )
        
        response_domain = understanding_domain or advice.domain
        response_domains = []
        if isinstance(response_domain, str) and response_domain:
            response_domains.append(response_domain)
        if hasattr(advice, "domains") and isinstance(advice.domains, list):
            for item in advice.domains:
                if item and item not in response_domains:
                    response_domains.append(item)

        # Build response using enhanced advisor output
        base_response = {
            "domain": response_domain,
            "domains": response_domains or [response_domain],
            "jurisdiction": advice.jurisdiction,
            "jurisdiction_detected": jurisdiction_result.jurisdiction,
            "jurisdiction_confidence": jurisdiction_result.confidence,
            "confidence": confidence,
            "legal_route": [
                "query_cleaning",
                "query_understanding",
                "query_expansion",
                "hybrid_retrieval",
                "cross_encoder_reranking",
                "legal_reasoning_engine",
                "clean_legal_advisor",
                "case_law_retriever",
            ],
            "statutes": statutes,
            "case_laws": case_laws,
            "constitutional_articles": [],
            "provenance_chain": [{
                "timestamp": datetime.now().isoformat(),
                "event": "query_processed",
                "agent": "clean_legal_advisor",
                "sections_found": sections_found,
                "case_laws_found": len(case_laws),
                "ontology_filtered": advice.ontology_filtered if hasattr(advice, 'ontology_filtered') else False,
                "domains": advice.domains if hasattr(advice, 'domains') else [advice.domain],
                "jurisdiction_detected": jurisdiction_result.jurisdiction,
                "jurisdiction_confidence": jurisdiction_result.confidence
            }],
            "reasoning_trace": {
                "legal_analysis": legal_analysis,
                "procedural_steps": advice.procedural_steps,
                "remedies": advice.remedies,
                "sections_found": sections_found,
                "case_laws_found": len(case_laws),
                "statute_source": statute_source,
                "query_understanding": getattr(advice, "query_understanding", {}),
                "retrieval_metadata": {
                    **(getattr(advice, "retrieval_metadata", {}) or {}),
                    "expanded_queries": expanded_queries,
                    "hybrid_sections_found": hybrid_result.get("sections_found", 0),
                    "reranked_top": len(top_sections),
                    "reasoning_added_sections": reasoning_added,
                },
                "query_expansion": {
                    "search_queries": expanded_queries,
                    "domain": understanding_domain,
                },
                "hybrid_retrieval": hybrid_result_public,
                "top_statutes": top_statutes,
                "reasoning_engine": {
                    "added_sections": reasoning_added,
                    "final_statutes": top_statutes,
                },
                "intent_domain_understanding": understanding,
                "query_cleaning": {
                    "original": request.query,
                    "cleaned": cleaned_query,
                },
                "jurisdiction_detection": {
                    "detected": jurisdiction_result.jurisdiction,
                    "confidence": jurisdiction_result.confidence,
                    "user_provided": jurisdiction_hint_str is not None
                },
                "confidence_factors": {
                    "sections_matched": sections_found,
                    "jurisdiction_confidence": confidence.jurisdiction,
                    "domain_confidence": confidence.domain,
                    "statute_match": confidence.statute_match
                }
            },
            "trace_id": advice.trace_id
        }
        
        # Enrich response with timeline, glossary, evidence_requirements
        enriched = enrich_response(base_response, cleaned_query, advice.domain, statutes, advice.jurisdiction)
        
        # Apply enforcement decision using enforcement engine
        enforcement_signal = EnforcementSignal(
            case_id=advice.trace_id,
            country=advice.jurisdiction,
            domain=response_domain,
            procedure_id=response_domain,
            original_confidence=advice.confidence_score,
            user_request=cleaned_query,
            jurisdiction_routed_to=advice.jurisdiction,
            trace_id=advice.trace_id
        )
        enforcement_result = enforcement_engine.make_enforcement_decision(enforcement_signal)
        enriched['enforcement_decision'] = enforcement_result.decision.value
        explanation_payload = generate_explanation_payload(
            query=cleaned_query,
            jurisdiction=advice.jurisdiction,
            domain=advice.domain,
            statutes=final_sections,
        )
        enriched["answer"] = explanation_payload["text"]
        enriched["answer_source"] = explanation_payload["source"]
        enriched["answer_model"] = explanation_payload.get("model")
        explanation_debug = {
            "source": explanation_payload.get("source"),
            "model": explanation_payload.get("model"),
        }
        if explanation_payload.get("reason"):
            explanation_debug["reason"] = explanation_payload.get("reason")
        if explanation_payload.get("error"):
            explanation_debug["error"] = explanation_payload.get("error")
        if "reasoning_trace" in enriched and (explanation_debug.get("reason") or explanation_debug.get("error")):
            enriched["reasoning_trace"]["explanation_generation"] = explanation_debug
        
        # Cache the enriched response for downstream endpoints
        response_cache.set(enriched.get("trace_id", advice.trace_id), enriched)

        return NyayaResponse(**enriched)
        
    except Exception as e:
        raise HTTPException(
            status_code=500,
            detail={
                "error_code": "QUERY_PROCESSING_ERROR",
                "message": f"Error processing legal query: {str(e)}",
                "trace_id": str(uuid.uuid4())
            }
        )

def _build_qualified_analysis(query: str, statutes: List, jurisdiction: str) -> str:
    """Build legal analysis with fully qualified statute references"""
    if not statutes:
        return f"No specific legal provisions found for this query in {jurisdiction} jurisdiction. Please provide more specific details or consult a legal professional."
    
    analysis = f"Legal Analysis for {jurisdiction} Jurisdiction:\n\n"
    analysis += "Applicable Legal Provisions:\n"
    analysis += "=" * 50 + "\n\n"
    
    for i, statute in enumerate(statutes, 1):
        analysis += f"{i}. Section {statute.section} of {statute.act}, {statute.year}:\n"
        analysis += f"   {statute.title}\n\n"
    
    return analysis

def _calculate_structured_confidence(
    sections_count: int,
    base_confidence: float,
    domain: str,
    query: str
) -> ConfidenceSchema:
    """Calculate structured confidence scores"""
    # Statute match confidence
    statute_match = min(0.95, 0.3 + (sections_count * 0.1)) if sections_count > 0 else 0.3
    
    # Domain confidence
    domain_keywords = {
        'criminal': ['crime', 'theft', 'murder', 'assault', 'terrorism'],
        'family': ['divorce', 'marriage', 'custody', 'alimony'],
        'civil': ['property', 'contract', 'consumer', 'employment']
    }
    
    domain_conf = 0.7
    if domain in domain_keywords:
        query_lower = query.lower()
        matches = sum(1 for kw in domain_keywords[domain] if kw in query_lower)
        domain_conf = min(0.95, 0.7 + (matches * 0.05))
    
    # Procedural match (placeholder)
    procedural_match = 0.8
    
    # Overall confidence
    overall = (base_confidence + statute_match + domain_conf) / 3
    
    return ConfidenceSchema(
        overall=min(0.95, overall),
        jurisdiction=base_confidence,
        domain=domain_conf,
        statute_match=statute_match,
        procedural_match=procedural_match
    )

@router.post("/multi_jurisdiction", response_model=MultiJurisdictionResponse)
async def multi_jurisdiction_query(request: MultiJurisdictionRequest):
    """Multi Jurisdiction Query"""
    return MultiJurisdictionResponse(
        comparative_analysis={},
        confidence=0.5,
        trace_id=str(uuid.uuid4())
    )

@router.post("/explain_reasoning", response_model=ExplainReasoningResponse)
async def explain_reasoning(request: ExplainReasoningRequest):
    """Explain Reasoning"""
    return ExplainReasoningResponse(
        trace_id=request.trace_id,
        explanation={"message": "Reasoning explanation"},
        reasoning_tree={"root": "explanation_tree"},
        constitutional_articles=[]
    )

@router.post("/feedback", response_model=FeedbackResponse)
async def submit_feedback(request: FeedbackRequest):
    """Submit Feedback"""
    return FeedbackResponse(
        status="received",
        trace_id=request.trace_id,
        message="Feedback submitted successfully"
    )

@router.get("/trace/{trace_id}", response_model=TraceResponse)
async def get_trace(trace_id: str):
    """Get Trace"""
    return TraceResponse(
        trace_id=trace_id,
        event_chain=[],
        agent_routing_tree={},
        jurisdiction_hops=[],
        rl_reward_snapshot={},
        context_fingerprint="mock_fingerprint",
        nonce_verification=True,
        signature_verification=True
    )

# ═══════════════════════════════════════════════════════════════
# NEW INTEGRATION ENDPOINTS (consumed by frontend components)
# ═══════════════════════════════════════════════════════════════

@router.get("/case_summary")
async def get_case_summary(trace_id: str = Query(..., description="Trace ID from a previous /query call")):
    """Return a summarised view of a cached query response."""
    cached = response_cache.get(trace_id)
    if not cached:
        raise HTTPException(status_code=404, detail={"error": "trace_id not found in cache", "trace_id": trace_id})
    statutes = cached.get("statutes", [])
    statute_list = []
    for s in (statutes or []):
        if isinstance(s, dict):
            statute_list.append({"act": s.get("act"), "section": s.get("section"), "title": s.get("title")})
        else:
            statute_list.append({"act": getattr(s, "act", ""), "section": getattr(s, "section", ""), "title": getattr(s, "title", "")})
    return {
        "trace_id": trace_id,
        "jurisdiction": cached.get("jurisdiction_detected") or cached.get("jurisdiction"),
        "domain": cached.get("domain"),
        "confidence": cached.get("confidence"),
        "enforcement_decision": cached.get("enforcement_decision"),
        "key_statutes": statute_list[:5],
        "summary_text": (cached.get("reasoning_trace") or {}).get("legal_analysis", "")[:500]
    }


@router.get("/legal_routes")
async def get_legal_routes(trace_id: str = Query(..., description="Trace ID from a previous /query call")):
    """Return the legal processing route for a cached query."""
    cached = response_cache.get(trace_id)
    if not cached:
        raise HTTPException(status_code=404, detail={"error": "trace_id not found in cache", "trace_id": trace_id})
    legal_route = cached.get("legal_route", [])
    routes = []
    for step in legal_route:
        routes.append({
            "name": step.replace("_", " ").title() if isinstance(step, str) else str(step),
            "description": f"Processing stage: {step}",
            "status": "completed"
        })
    return {
        "trace_id": trace_id,
        "routes": routes,
        "procedural_steps": (cached.get("reasoning_trace") or {}).get("procedural_steps", []),
        "remedies": (cached.get("reasoning_trace") or {}).get("remedies", [])
    }


@router.get("/timeline")
async def get_timeline(trace_id: str = Query(..., description="Trace ID from a previous /query call")):
    """Return the procedural timeline for a cached query."""
    cached = response_cache.get(trace_id)
    if not cached:
        raise HTTPException(status_code=404, detail={"error": "trace_id not found in cache", "trace_id": trace_id})
    timeline = cached.get("timeline", [])
    steps = []
    for idx, item in enumerate(timeline, 1):
        if isinstance(item, dict):
            steps.append({"milestone": idx, "step": item.get("step", ""), "eta": item.get("eta", "Varies")})
        else:
            steps.append({"milestone": idx, "step": str(item), "eta": "Varies"})
    return {
        "trace_id": trace_id,
        "steps": steps
    }


@router.get("/glossary")
async def get_glossary(trace_id: str = Query(..., description="Trace ID from a previous /query call")):
    """Return the legal glossary terms for a cached query."""
    cached = response_cache.get(trace_id)
    if not cached:
        raise HTTPException(status_code=404, detail={"error": "trace_id not found in cache", "trace_id": trace_id})
    glossary = cached.get("glossary", [])
    terms = []
    for item in glossary:
        if isinstance(item, dict):
            terms.append({"term": item.get("term", ""), "definition": item.get("definition", "")})
        else:
            terms.append({"term": str(item), "definition": ""})
    return {
        "trace_id": trace_id,
        "terms": terms
    }


@router.get("/jurisdiction_info")
async def get_jurisdiction_info(jurisdiction: str = Query(..., description="Jurisdiction code: India, UK, UAE, KSA")):
    """Return static metadata for a jurisdiction."""
    JURISDICTION_DATA = {
        "India": {
            "code": "IN",
            "name": "Republic of India",
            "legal_system": "Common Law (derived from British system)",
            "court_structure": "Supreme Court → High Courts → District Courts → Magistrate Courts",
            "key_acts": ["Indian Penal Code 1860", "Bharatiya Nyaya Sanhita 2023", "Code of Criminal Procedure 1973", "Code of Civil Procedure 1908", "Indian Evidence Act 1872", "Information Technology Act 2000"]
        },
        "UK": {
            "code": "GB",
            "name": "United Kingdom",
            "legal_system": "Common Law",
            "court_structure": "Supreme Court → Court of Appeal → High Court → Crown/County Courts → Magistrates' Courts",
            "key_acts": ["Criminal Justice Act 2003", "Theft Act 1968", "Human Rights Act 1998", "Civil Procedure Rules 1998", "Equality Act 2010"]
        },
        "UAE": {
            "code": "AE",
            "name": "United Arab Emirates",
            "legal_system": "Civil Law (with Sharia influence)",
            "court_structure": "Federal Supreme Court → Courts of Appeal → Courts of First Instance",
            "key_acts": ["Federal Penal Code", "Civil Transactions Law", "Labour Law", "Personal Status Law", "Commercial Transactions Law"]
        },
        "KSA": {
            "code": "SA",
            "name": "Kingdom of Saudi Arabia",
            "legal_system": "Sharia Law (with Royal Decrees)",
            "court_structure": "Supreme Court → Courts of Appeal → General/Criminal Courts",
            "key_acts": ["Basic Law of Governance", "Law of Procedure before Sharia Courts", "Labour Law", "Anti-Cyber Crime Law"]
        }
    }
    # Normalise key lookup
    key = jurisdiction.strip()
    data = JURISDICTION_DATA.get(key)
    if not data:
        # Try case-insensitive match
        for k, v in JURISDICTION_DATA.items():
            if k.lower() == key.lower():
                data = v
                break
    if not data:
        raise HTTPException(status_code=404, detail={"error": f"Unknown jurisdiction: {jurisdiction}"})
    return data


@router.get("/enforcement_status")
async def get_enforcement_status(trace_id: str = Query(..., description="Trace ID from a previous /query call")):
    """Return the enforcement decision details for a cached query."""
    cached = response_cache.get(trace_id)
    if not cached:
        raise HTTPException(status_code=404, detail={"error": "trace_id not found in cache", "trace_id": trace_id})
    provenance = cached.get("provenance_chain", [{}])
    first_prov = provenance[0] if provenance else {}
    return {
        "trace_id": trace_id,
        "decision": cached.get("enforcement_decision", "UNKNOWN"),
        "jurisdiction_detected": first_prov.get("jurisdiction_detected"),
        "jurisdiction_confidence": first_prov.get("jurisdiction_confidence"),
        "timestamp": first_prov.get("timestamp"),
        "sections_found": first_prov.get("sections_found", 0),
        "domains": first_prov.get("domains", [])
    }


@router.post("/rl_signal")
async def submit_rl_signal(request: RLSignalRequest):
    """Accept a reinforcement learning signal from the frontend."""
    try:
        from rl_engine.reward_engine import RewardEngine
        reward_engine = RewardEngine()
        signal = {
            "trace_id": request.trace_id,
            "user_feedback": request.user_feedback,
            "outcome_tag": request.outcome_tag,
            "timestamp": datetime.utcnow().isoformat()
        }
        reward, should_learn, reason = reward_engine.compute_reward(signal)
        return {
            "accepted": should_learn,
            "reward_computed": reward,
            "reason": reason if reason else "signal_accepted",
            "trace_id": request.trace_id
        }
    except Exception as e:
        logger.warning("RL signal processing failed: %s", e)
        return {
            "accepted": False,
            "reward_computed": 0.0,
            "reason": f"processing_error: {str(e)}",
            "trace_id": request.trace_id
        }
