# FinPulse AI — REST API (v1)

Base URL: `http://127.0.0.1:8000` · Interactive docs: `/docs`

| Method | Path | Purpose |
|---|---|---|
| GET | /health | Liveness |
| GET | /api/v1/status | Model + demo portfolio status |
| GET | /api/v1/msmes | Paginated portfolio. Query: search, sector, health_band, trend_status, credit_readiness, confidence_status, anomaly_status, sort_by, sort_order, page, page_size |
| GET | /api/v1/msmes/{id} | Summary |
| GET | /api/v1/msmes/{id}/health-card | Full Financial Health Card (identity, score, exact components, 6 dimensions, confidence, readiness, anomaly, trend, model applicability, disclaimers) |
| GET | /api/v1/msmes/{id}/twin | Temporal Twin (real monthly re-scoring) |
| GET | /api/v1/msmes/{id}/explanation | ml_factors vs financial_health_signals; honest explanation_mode |
| GET | /api/v1/msmes/{id}/simulate/current | Read-only current simulator values + allowed ranges for the four editable fields |
| POST | /api/v1/msmes/{id}/simulate | Body: receivable_days, cash_reserve, customer_concentration, debt_service_ratio (≥1 required). 422 on invalid ranges. |
| GET | /api/v1/analytics/portfolio | Calculated portfolio KPIs + attention signals |
| GET | /api/v1/metadata/model | Model card + application limits |
| GET | /api/v1/metadata/scoring | Exact formula, weights, bands |
| GET | /api/v1/metadata/data-sources | Provenance definitions + limitations |

Errors: 404 unknown MSME; 422 invalid simulation; no stack traces exposed.
`model_application_status` ∈ applied · not_applicable_to_demo_schema · demo_fallback · artifact_unavailable.