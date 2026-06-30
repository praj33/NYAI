# Testing Guide — Phase V

## 1. Test matrix (module × type)

| Module | Type | Tests |
|--------|------|-------|
| `test_knowledge_repository.py` | unit | 10 |
| `test_ingestion_pipeline.py` | unit | 8 |
| `test_workspace_apis.py` | API (TestClient) | 8 |
| `test_graph_runtime.py` | API + traversal | 8 |
| `test_promotion_pipeline.py` | API + state machine | 8 |
| `test_knowledge_integration.py` | integration (Phase IV ↔ V) | 6 |
| `test_replay_knowledge.py` | replay (stored-record) | 5 |
| `test_determinism_knowledge.py` | determinism / hash | 5 |
| `test_knowledge_failure.py` | failure / validation | 8 |
| **Total (new)** | | **66** |

Backward-compat baseline (Phase IV): `test_evidence_infrastructure.py` (14),
`test_production_hardening.py` (15), `test_tantra_convergence.py` (6) = **35**.

## 2. Run all Phase V tests

```powershell
cd backend
python -m pytest tests/test_knowledge_repository.py tests/test_ingestion_pipeline.py `
  tests/test_workspace_apis.py tests/test_graph_runtime.py tests/test_promotion_pipeline.py `
  tests/test_knowledge_integration.py tests/test_replay_knowledge.py `
  tests/test_determinism_knowledge.py tests/test_knowledge_failure.py -v
```

## 3. Run Phase IV + Phase V together (recommended gate)

```powershell
cd backend
python -m pytest tests/test_evidence_infrastructure.py tests/test_production_hardening.py `
  tests/test_tantra_convergence.py tests/test_knowledge_repository.py `
  tests/test_ingestion_pipeline.py tests/test_workspace_apis.py tests/test_graph_runtime.py `
  tests/test_promotion_pipeline.py tests/test_knowledge_integration.py `
  tests/test_replay_knowledge.py tests/test_determinism_knowledge.py `
  tests/test_knowledge_failure.py -v
```

Latest result: **101 passed** (35 Phase IV + 66 Phase V).

## 4. Test isolation notes

- Unit suites (`repository`, `ingestion`, `determinism`) build **isolated**
  repositories/logs via `tmp_path`, so `count()` and duplicate-detection
  assertions are deterministic and independent of the shared on-disk store.
- API suites set `RATE_LIMIT_PER_MINUTE`/`RATE_LIMIT_BURST` high via a
  `monkeypatch` autouse fixture (auto-restored after each test) so multi-request
  tests don't trip the limiter; the shared `conftest.py` resets limiter buckets
  between tests.
- All evidence assertions read the shared `OutputBucket`, exercising the real
  Phase IV ↔ Phase V linkage.

## 5. Coverage intent

Targets 100% of new Phase V modules across happy-path, validation-failure,
integrity-tamper, cyclic-graph, invalid-state-transition, and missing-auth
cases. No external services required (no network, no DB) — all stores are local
JSONL created on first use.

## 6. What each new suite proves (selected)

- **repository** — registration, versioning, integrity verify/tamper, evidence
  emission, storage-agnostic backend.
- **ingestion** — schema rejection, duplicate rejection, version diff, PENDING
  status, ingestion evidence.
- **workspace** — upload/update/annotation/version-history/compare/audit, auth.
- **graph** — entity/relationship registration, dependency/impact/citation/path,
  cycle-safe traversal, GRAPH_OP evidence.
- **promotion** — valid/invalid transitions, rollback-creates-version, audit
  trail, PROMOTE/ROLLBACK evidence, ARCHIVED terminal.
- **integration** — knowledge evidence appears in `/evidence/search`, verifiable,
  `/nyaya/query` unaffected, health includes `knowledge_repository`, all evidence
  endpoints backward-compatible, chain integrity intact.
- **replay / determinism / failure** — stored-record replay, deterministic
  hashes, sequential versions, unique evidence traces, 404/422/400 fail-closed
  paths.
