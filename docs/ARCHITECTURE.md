# Architecture

Adapters (public_dataset / synthetic_demo / future_sandbox stub)
→ FinPulseFinancials (standardized schema)
→ FinPulseOrchestrator (singleton; loads demo JSON once, fits Isolation Forest once)
→ Phase 1 engines: six dimensions · FinPulse Score · Data Confidence · Temporal Twin ·
  anomaly · counterfactual · credit readiness · explanation
→ FastAPI /api/v1 (thin routers, no scoring logic)
→ Next.js frontend (App Router, typed API client)

Principle: **Swap the connector, not the intelligence engine.**
ML constraint: survey-trained model ↔ standardized demo schema are incompatible;
demo cards use the documented fallback (risk_probability = None) and expose
model_application_status honestly. No retraining ever happens in a request.
DB (SQLAlchemy/SQLite, PostgreSQL via DATABASE_URL) stays ingestion-ready; the
deterministic demo JSON is the hackathon portfolio source of truth (documented).