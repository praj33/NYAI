# Nyaya AI — System Map

> Generated: April 16, 2026
> Repo: https://github.com/praj33/NYAI.git

---

## 1. Repository Structure

```
NYAI-Integrated/
├── backend/                          # Python/FastAPI Backend
│   ├── api/                          # API Layer (entry point)
│   │   ├── main.py                   # ← BACKEND ENTRY POINT (FastAPI app)
│   │   ├── router.py                 # Core /nyaya/* endpoints (12 routes)
│   │   ├── schemas.py                # Pydantic request/response contracts
│   │   ├── procedure_router.py       # /nyaya/procedures/* endpoints
│   │   └── debug_router.py           # Dev-only debug endpoints
│   │
│   ├── clean_legal_advisor.py        # Core Decision Engine (EnhancedLegalAdvisor)
│   │
│   ├── services/                     # Service Layer
│   │   ├── retriever.py              # HybridLegalRetriever (BM25 + FAISS)
│   │   ├── query_cleaner.py          # Query normalization
│   │   ├── query_understanding.py    # NLP intent/domain detection
│   │   ├── query_expander.py         # Multi-query expansion
│   │   ├── reranker.py               # Cross-encoder reranking
│   │   ├── legal_reasoner.py         # Rule-based legal reasoning
│   │   └── explainer.py              # Groq LLM explanation generator
│   │
│   ├── bm25_search.py                # Custom BM25 implementation
│   │
│   ├── enforcement_engine/           # Sovereign Enforcement
│   │   ├── engine.py                 # SovereignEnforcementEngine (singleton)
│   │   ├── decision_model.py         # Decision enums & data models
│   │   ├── rules.py                  # 6 enforcement rules
│   │   └── signer.py                 # HMAC signing
│   │
│   ├── enforcement_provenance/       # Audit Trail
│   │   └── ledger.py                 # Hash-chained enforcement ledger
│   │
│   ├── provenance_chain/             # General Provenance
│   │   └── hash_chain_ledger.py      # SHA256 hash-chain ledger
│   │
│   ├── governed_execution/           # Governed Pipeline
│   │   └── pipeline.py               # Enforcement + RL gating wrapper
│   │
│   ├── rl_engine/                    # Reinforcement Learning
│   │   ├── reward_engine.py          # Hardened reward computation
│   │   ├── feedback_api.py           # Feedback ingestion
│   │   └── confidence_tracker.py     # EMA confidence tracking
│   │
│   ├── sovereign_agents/             # Multi-Agent System
│   │   ├── base_agent.py             # BaseAgent ABC
│   │   ├── legal_agent.py            # LegalAgent
│   │   └── constitutional_agent.py   # ConstitutionalAgent
│   │
│   ├── jurisdiction_router/          # Jurisdiction Routing
│   │   ├── router.py                 # Regex-based routing
│   │   ├── confidence_aggregator.py  # Weighted confidence scoring
│   │   ├── fallback_manager.py       # Auto-escalation
│   │   └── resolver_pipeline.py      # Agent dispatch
│   │
│   ├── raj_adapter/                  # External Schema Integration
│   │   ├── schema_consumer.py        # Raj schema consumer
│   │   └── enforcement_integration.py # 3 Raj enforcement rules
│   │
│   ├── core/                         # Core Modules
│   │   ├── jurisdiction/detector.py  # JurisdictionDetector
│   │   ├── caselaw/                  # Case law loading + retrieval
│   │   ├── response/enricher.py      # Response enrichment
│   │   ├── ontology/                 # Legal ontology
│   │   ├── vector/faiss_index.py     # FAISS index
│   │   ├── llm/groq_client.py        # Groq LLM client
│   │   ├── addons/                   # Offense subtypes + dowry layer
│   │   └── scrapers/                 # Supreme Court scraper
│   │
│   ├── db/                           # Legal Database (52 files)
│   ├── data/                         # Prebuilt FAISS index + case law
│   ├── procedures/                   # 16 procedure files (4 jurisdictions × 4 domains)
│   ├── raj_schemas/                  # External compliance schemas
│   ├── tests/                        # ~30 test files
│   ├── .env                          # Config (GITIGNORED)
│   ├── .env.example                  # Template
│   └── requirements.txt              # Python dependencies
│
├── frontend/                         # React/Vite Frontend
│   ├── src/
│   │   ├── main.jsx                  # ← FRONTEND ENTRY POINT
│   │   ├── App.jsx                   # Root component + routing
│   │   ├── components/               # 48 React components
│   │   │   ├── LegalQueryCard.jsx    # Primary query interface
│   │   │   ├── LegalDecisionDocument.jsx # Decision document renderer
│   │   │   ├── DecisionPage.jsx      # Standalone decision page
│   │   │   ├── Galaxy.jsx            # OGL starfield background
│   │   │   ├── GlassSurface.jsx      # Glassmorphism component
│   │   │   ├── EnforcementStatusCard.jsx # Enforcement visualization
│   │   │   ├── FeedbackButtons.jsx   # RL feedback signals
│   │   │   └── ...                   # 40+ more components
│   │   ├── services/                 # API Service Layer
│   │   │   ├── nyayaApi.js           # Primary API client (718 lines)
│   │   │   ├── apiService.js         # Generic fetch wrapper
│   │   │   ├── offlineStore.js       # localStorage persistence
│   │   │   └── apiConfig.ts          # Base URL config
│   │   ├── hooks/                    # Custom React Hooks
│   │   │   ├── useResiliency.js      # Offline detection + auto-sync
│   │   │   └── ...
│   │   └── lib/                      # Utilities
│   ├── vercel.json                   # Vercel deployment config
│   ├── vite.config.js                # Vite dev server + proxy config
│   └── package.json                  # Node dependencies
│
├── DISCLOSURE_REPORT.md              # Full system analysis
├── INTEGRATION_PLAN.md               # Integration plan
├── .gitignore                        # Excludes venv, node_modules, .env
└── system_map.md                     # THIS FILE
```

---

## 2. Entry Points

| System | File | How to Run |
|--------|------|------------|
| **Backend** | `backend/api/main.py` | `python -m uvicorn api.main:app --host 0.0.0.0 --port 8000` |
| **Frontend** | `frontend/src/main.jsx` | `npm run dev` (Vite on port 3000) |

---

## 3. All API Endpoints (25 total)

### Core Endpoints (12 — in `router.py`)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/nyaya/query` | Primary legal query |
| POST | `/nyaya/multi_jurisdiction` | Multi-jurisdiction comparison |
| POST | `/nyaya/explain_reasoning` | Explain reasoning for trace |
| POST | `/nyaya/feedback` | Submit user feedback |
| GET | `/nyaya/trace/{trace_id}` | Get trace details |
| GET | `/nyaya/case_summary` | Case summary (cached) |
| GET | `/nyaya/legal_routes` | Legal processing route |
| GET | `/nyaya/timeline` | Procedural timeline |
| GET | `/nyaya/glossary` | Legal glossary |
| GET | `/nyaya/jurisdiction_info` | Jurisdiction metadata |
| GET | `/nyaya/enforcement_status` | Enforcement decision |
| POST | `/nyaya/rl_signal` | RL signal ingestion |

### Procedure Endpoints (8 — in `procedure_router.py`)
| Method | Path | Purpose |
|--------|------|---------|
| POST | `/nyaya/procedures/analyze` | Procedure analysis |
| GET | `/nyaya/procedures/summary/{country}/{domain}` | Procedure summary |
| POST | `/nyaya/procedures/evidence/assess` | Evidence assessment |
| POST | `/nyaya/procedures/failure/analyze` | Failure analysis |
| POST | `/nyaya/procedures/compare` | Cross-country comparison |
| GET | `/nyaya/procedures/list` | List all procedures |
| GET | `/nyaya/procedures/schemas` | Get schemas |
| GET | `/nyaya/procedures/enhanced_analysis/{jur}/{dom}` | Enhanced analysis |

### System Endpoints (3 — in `main.py`)
| Method | Path | Purpose |
|--------|------|---------|
| GET | `/` | Root info |
| GET | `/health` | Health check |
| GET | `/docs` | Swagger UI |

---

## 4. Canonical Execution Flow

```
User Query (Frontend)
    │
    ▼
LegalQueryCard.jsx → nyayaApi.js → POST /nyaya/query
    │
    ▼ ─── BACKEND PIPELINE ───
    │
    ├── 1. Query Cleaning (query_cleaner.py)
    ├── 2. Query Understanding (query_understanding.py)
    ├── 3. Query Expansion (query_expander.py)
    ├── 4. Hybrid Retrieval (retriever.py — BM25 + FAISS)
    ├── 5. Cross-Encoder Reranking (reranker.py — 8s timeout)
    ├── 6. Legal Reasoning Rules (legal_reasoner.py)
    ├── 7. EnhancedLegalAdvisor (clean_legal_advisor.py)
    ├── 8. Case Law Retrieval (caselaw/retriever.py)
    ├── 9. Response Enrichment (enricher.py — timeline, glossary, evidence)
    ├── 10. Groq LLM Answer (groq_client.py — llama-3.3-70b, 20s timeout)
    ├── 11. Enforcement Decision (engine.py — 9 rules)
    └── 12. Response Cache (ResponseCache — keyed by trace_id)
    │
    ▼
NyayaResponse JSON → Frontend
    │
    ├── LegalDecisionDocument.jsx (structured decision)
    ├── EnforcementStatusCard.jsx (ALLOW/RESTRICT/REDIRECT badge)
    ├── FeedbackButtons.jsx → POST /nyaya/rl_signal
    └── Downstream: /case_summary, /timeline, /glossary, /legal_routes, /enforcement_status
```

---

## 5. Module Dependencies

```
api/main.py
  ├── api/router.py
  │     ├── clean_legal_advisor.py (EnhancedLegalAdvisor)
  │     ├── core/jurisdiction/detector.py
  │     ├── core/caselaw/loader.py + retriever.py
  │     ├── core/response/enricher.py
  │     ├── services/query_cleaner.py
  │     ├── services/query_understanding.py
  │     ├── services/query_expander.py
  │     ├── services/retriever.py (HybridLegalRetriever)
  │     ├── services/reranker.py
  │     ├── services/legal_reasoner.py
  │     ├── services/explainer.py
  │     ├── enforcement_engine/engine.py
  │     │     ├── enforcement_engine/rules.py (6 rules)
  │     │     ├── enforcement_engine/decision_model.py
  │     │     └── enforcement_engine/signer.py
  │     └── rl_engine/reward_engine.py
  ├── api/procedure_router.py
  └── api/debug_router.py
```

---

## 6. Data Assets

| Category | Location | Count | Size |
|----------|----------|-------|------|
| Legal DB (statutes) | `backend/db/` | 52 files | ~2MB |
| Procedure data | `backend/procedures/data/` | 16 files | ~85KB |
| FAISS index | `backend/data/vector_index/` | 2 files | ~3.6MB |
| Case law | `backend/data/caselaw/` | 2 files | ~9KB |
| Offense subtypes | `backend/core/addons/` | 2 files | ~65KB |
| Raj schemas | `backend/raj_schemas/` | 3 files | ~3KB |
