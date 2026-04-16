# Nyaya AI — System Architecture

---

## High-Level Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                         FRONTEND (React/Vite)                       │
│                                                                     │
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────────┐  │
│  │ LegalQuery   │  │ Decision     │  │ Enforcement    Feedback  │  │
│  │ Card.jsx     │  │ Document.jsx │  │ StatusCard.jsx Buttons   │  │
│  └──────┬───────┘  └──────┬───────┘  └──────┬──────────┬───────┘  │
│         │                  │                  │          │          │
│         ▼                  ▼                  ▼          ▼          │
│  ┌──────────────────────────────────────────────────────────────┐  │
│  │                     nyayaApi.js (Unified API Client)         │  │
│  │  interceptors · timeout · retry · offline detection          │  │
│  └──────────────────────────┬───────────────────────────────────┘  │
│                              │                                      │
│  ┌──────────────────────────┐│┌─────────────────────────────────┐  │
│  │ useResiliency.js         │││ offlineStore.js                 │  │
│  │ health polling · sync    │││ localStorage persistence        │  │
│  └──────────────────────────┘│└─────────────────────────────────┘  │
└──────────────────────────────┼──────────────────────────────────────┘
                               │ HTTP (JSON)
                               ▼
┌─────────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (FastAPI)                           │
│                      backend/api/main.py                            │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────┐      │
│  │ CORS · Trace ID Middleware · Exception Handler            │      │
│  └───────────────────────────────────────────────────────────┘      │
│                                                                     │
│  ┌──────────────────┐  ┌─────────────────┐  ┌──────────────────┐  │
│  │ router.py        │  │ procedure_      │  │ debug_router.py  │  │
│  │ 12 endpoints     │  │ router.py       │  │ (dev only)       │  │
│  │ + ResponseCache  │  │ 8 endpoints     │  │                  │  │
│  └────────┬─────────┘  └─────────────────┘  └──────────────────┘  │
└───────────┼─────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                     QUERY PIPELINE                                   │
│                                                                     │
│  ┌──────────┐  ┌──────────────┐  ┌──────────────┐  ┌───────────┐  │
│  │ Query    │→│ Query        │→│ Query        │→│ Hybrid    │  │
│  │ Cleaner  │  │ Understanding│  │ Expander     │  │ Retriever │  │
│  └──────────┘  └──────────────┘  └──────────────┘  └─────┬─────┘  │
│                                                           │         │
│              ┌─────────────────────────────────────┐      │         │
│              │        HYBRID SEARCH                 │      │         │
│              │                                      │◄─────┘         │
│              │  ┌──────────┐    ┌───────────────┐  │                │
│              │  │ BM25     │    │ FAISS         │  │                │
│              │  │ (sparse) │    │ BAAI/bge-m3   │  │                │
│              │  │ BM25Okapi│    │ (dense)       │  │                │
│              │  └────┬─────┘    └──────┬────────┘  │                │
│              │       └───────┬─────────┘           │                │
│              │          Score Fusion                │                │
│              └──────────────┬──────────────────────┘                │
│                              │                                      │
│  ┌──────────────┐  ┌────────▼──────┐  ┌──────────────────────────┐ │
│  │ Cross-Encoder│←│ Reranked     │→│ Legal Reasoning Rules    │ │
│  │ Reranker     │  │ Candidates   │  │ (domain-specific logic)  │ │
│  └──────────────┘  └──────────────┘  └────────────┬─────────────┘ │
│                                                     │               │
│  ┌──────────────────────────────────────────────────▼─────────────┐ │
│  │              EnhancedLegalAdvisor                               │ │
│  │              (clean_legal_advisor.py)                           │ │
│  │              9129 sections · 99 acts · 3 jurisdictions         │ │
│  └──────────────────────────────────────┬────────────────────────┘ │
│                                          │                         │
│  ┌──────────┐  ┌─────────────┐  ┌───────▼──────┐  ┌───────────┐  │
│  │ Case Law │  │ Response    │  │ Groq LLM    │  │ Addon     │  │
│  │ Retriever│  │ Enricher    │  │ llama-3.3   │  │ Subtypes  │  │
│  │ (23 cases)│  │ (timeline,  │  │ -70b        │  │ Resolver  │  │
│  │          │  │  glossary)  │  │ (20s timeout)│  │           │  │
│  └──────────┘  └─────────────┘  └──────────────┘  └───────────┘  │
└─────────────────────────────────────────────────────────────────────┘
            │
            ▼
┌─────────────────────────────────────────────────────────────────────┐
│                   ENFORCEMENT LAYER                                  │
│                                                                     │
│  ┌───────────────────────────────────────────────────────────────┐  │
│  │              SovereignEnforcementEngine                       │  │
│  │              (singleton, thread-safe)                         │  │
│  │                                                               │  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│  │
│  │  │ INTENT-001  │ │ CONST-001   │ │ JURIS-001               ││  │
│  │  │ Intent      │ │ Constitution│ │ Jurisdiction             ││  │
│  │  │ Detection   │ │ Compliance  │ │ Boundary                 ││  │
│  │  └─────────────┘ └─────────────┘ └─────────────────────────┘│  │
│  │  ┌─────────────┐ ┌─────────────┐ ┌─────────────────────────┐│  │
│  │  │ SAFETY-001  │ │ CONF-001    │ │ PROC-001                ││  │
│  │  │ System      │ │ Confidence  │ │ Procedure                ││  │
│  │  │ Safety      │ │ Threshold   │ │ Integrity                ││  │
│  │  └─────────────┘ └─────────────┘ └─────────────────────────┘│  │
│  │  ┌─────────────────────────────────────────────────────────┐ │  │
│  │  │ Raj Rules: RAJ-FAILURE-001 · RAJ-EVIDENCE-001 ·        │ │  │
│  │  │            RAJ-COMPLIANCE-001                           │ │  │
│  │  └─────────────────────────────────────────────────────────┘ │  │
│  │                                                               │  │
│  │  Decision: ALLOW | ALLOW_INFORMATIONAL | SAFE_REDIRECT |     │  │
│  │            RESTRICT                                           │  │
│  └───────────────────────────────────────────────────────────────┘  │
│                                                                     │
│  ┌───────────────────┐  ┌───────────────────────────────────────┐  │
│  │ RL Engine         │  │ Provenance Ledger                     │  │
│  │ RewardEngine      │  │ Hash-chained, append-only,            │  │
│  │ +0.05/-0.08 delta │  │ tamper-detection, integrity verify    │  │
│  │ volatility cap    │  │                                       │  │
│  └───────────────────┘  └───────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────────┘
```

---

## Technology Stack

| Layer | Technology | Details |
|-------|-----------|---------|
| **Frontend** | React 18 + Vite 7 | JSX components, GSAP animations, OGL 3D |
| **API Gateway** | FastAPI + Uvicorn | Async, CORS, trace middleware |
| **Sparse Search** | BM25Okapi (rank-bm25) | k1=1.5, b=0.75 |
| **Dense Search** | FAISS + bge-m3 | Inner Product similarity |
| **Reranking** | Cross-Encoder | sentence-transformers |
| **LLM** | Groq API | llama-3.3-70b-versatile + llama-3.1-8b |
| **Enforcement** | Custom rule engine | 9 deterministic rules, singleton |
| **RL** | Custom RewardEngine | Hardened with anomaly detection |
| **Provenance** | SHA256 hash-chain | Append-only, tamper-resistant |
| **Data** | JSON files + FAISS index | 52 legal DB files, pre-built vectors |

---

## Deployment Architecture

```
┌──────────────────────┐         ┌──────────────────────┐
│     VERCEL            │  HTTP   │     RENDER            │
│     (Frontend)        │────────▶│     (Backend)         │
│                       │         │                       │
│  React/Vite Build     │         │  Python 3.11          │
│  Static Assets (CDN)  │         │  FastAPI + Uvicorn    │
│                       │         │  torch + FAISS        │
│  Env:                 │         │  sentence-transformers│
│  VITE_API_URL=        │         │                       │
│    <render-url>       │         │  Env:                 │
│                       │         │  GROQ_API_KEY=        │
│  Domain:              │         │  HMAC_SECRET_KEY=     │
│  nyaya-ai.vercel.app  │         │  FRONTEND_URL=        │
│                       │         │    <vercel-url>       │
└──────────────────────┘         └──────────────────────┘
```
