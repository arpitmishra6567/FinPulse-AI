# FinPulse AI — Phase 2 Verification Report

STATUS: PASS WITH LIMITATIONS

## Dataset / provenance
- Source file: `backend/data/raw/Finanical_data_sme.csv`
- Provenance: `public_dataset`
- Shape: 10,000 rows × 33 columns
- Target: `Financial_Distress`
- Target distribution before cleaning: `0.0=6620`, `1.0=2880`, `NaN=500`
- Cleaning summary: removed `500` missing-target rows and `98` duplicates; final training rows `9402`
- Demo portfolio: `backend/data/demo/demo_msmes.json`, `100` MSMEs, deterministic sha256 `78e0ac4dbfe43ab25b7b23ae57bc7ab31b59df351bd78cf4c156709f42e10c98`

## Model artifact / status (stored artifacts only; no retraining)
- Artifact dir: `backend/ml/artifacts/`
- Model status: `trained_model`
- Model name: `logistic_regression`
- Training date: `2026-07-07`
- Dataset name: `Finanical_data_sme.csv`
- Raw record count: `10000`
- Training record count: `7521`
- Target interpretation: `1 = financial distress / higher financial risk`
- Positive probability index: `1`
- Validation method: `stratified train/test split test_size=0.20 random_state=42 (no genuine chronology in dataset)`
- Stored metrics exactly found in `model_metrics.json`:
  - accuracy `0.5635300372142478`
  - roc_auc `0.6199745424852299`
  - pr_auc `0.4024246236241368`
  - precision `0.36550976138828634`
  - recall `0.5881326352530541`
  - f1 `0.4508361204013378`
  - brier `0.24071644273398857`
  - confusion_matrix `[[723,585],[236,337]]`
- Stored comparison: logistic regression `selected`; random forest and xgboost `rejected`
- Leakage audit: `Decision_Loan_Approval` excluded; `decision_loan_approval_excluded=true`

## Demo / model applicability
- Demo cards use `synthetic_demo` standardized financial schema
- Survey-trained model applicability for demo: `not_applicable_to_demo_schema`
- Verified live `risk_probability=null` on demo Health Card
- Verified fallback contract: `ml_component == dimension_composite`
- Data Confidence remains separate from FinPulse Score

## Exact test / verification results
- Pytest: `20 passed, 1 warning in 3.90s`
- Warning: Starlette/TestClient `httpx` deprecation warning only
- Live endpoint probe MSME ID: `DEMO-036`
- 12 required endpoints: PASS (`200` on `/health`, `/api/v1/status`, `/api/v1/msmes`, `/api/v1/msmes/{id}`, `/health-card`, `/twin`, `/explanation`, `POST /simulate`, `/analytics/portfolio`, `/metadata/model`, `/metadata/scoring`, `/metadata/data-sources`)
- Additional read-only simulator endpoint: `GET /api/v1/msmes/{id}/simulate/current` → `200`
- Unknown ID checks: summary/health-card/twin/explanation/simulate all `404`
- Invalid simulation checks: empty body `422`; out-of-range body `422`
- Pagination/filter/sort probe: page size `5`, returned `5`, total `100`; `health_band=Critical` all matched; ascending score sort matched
- Health semantics: score `81.4` in range, `6` dimensions, all dimension scores in range, weights exactly `{dimensions:0.65, ml_risk:0.25, anomaly:0.10}`
- Explanation semantics: `rules_fallback`, `ml_factors=[]`, `financial_health_signals=6`
- Twin semantics: `12` score points, all within `0..100`
- Analytics reconciliation: `total_msmes=100`, band sum `100`
- Metadata semantics: dimension weight sum `1.0`; `public_dataset` and `synthetic_demo` provenance definitions present
- CORS: preflight from `http://localhost:3000` returned `200` with `access-control-allow-origin: http://localhost:3000`
- Prohibited claims absent from representative live API payloads

## Integration / frontend verification
- API base is env-based with localhost fallback in `frontend/src/lib/api.ts`
- `frontend/.env.example` and `.env.local` both point to `http://127.0.0.1:8000`
- Frontend production route probe via `next start`: `/dashboard`, `/msmes`, `/msmes/DEMO-001`, `/msmes/DEMO-001/twin`, `/msmes/DEMO-001/explain`, `/msmes/DEMO-001/simulate`, `/transparency` all returned `200` HTML
- Dashboard integration path verified by source + live API availability: portfolio analytics endpoint healthy
- One MSME API-backed flow verified live: Health Card, Twin, Explanation, Simulation, and `simulate/current`
- Simulator current-value behavior verified in source + live API: `simulate/page.tsx` initializes sliders from `GET /simulate/current`; no arbitrary defaults are used when backend values exist
- Browser E2E unavailable in this session; no visual/browser claim is asserted beyond route and API-backed verification

## Lint / TypeScript / production build
- `npm run lint` → `✔ No ESLint warnings or errors`
- `npx tsc --noEmit` → clean exit `0`, no output
- `npm run build` → compiled successfully; generated routes `/`, `/dashboard`, `/msmes`, `/msmes/[msmeId]`, `/msmes/[msmeId]/explain`, `/msmes/[msmeId]/simulate`, `/msmes/[msmeId]/twin`, `/transparency`

## Bugs fixed in Parts 1 / 2
- Part 1 verified: demo generator low-confidence carry-value bug fix preserved
- Part 1 verified: read-only `GET /simulate/current` preserved and live
- Part 1 verified: simulator page initializes from backend current values and posts only changed fields
- Part 2 fix: refreshed `docs/API.md` to document `GET /api/v1/msmes/{id}/simulate/current`
- No additional backend/frontend logic defect was reproduced during Part 2 executable checks

## Part 2 modified files
- `docs/API.md`
- `VERIFICATION_REPORT.md`

## Honest limitations
- Browser automation / visual click-through unavailable; API-backed integration and HTTP route verification completed instead
- Test bundle contains `20` backend tests, not `24`
- `next@14.2.5` advisory remains; version left pinned per repository contract

## Windows run commands
- Backend:
  - `python -m venv .venv`
  - `.venv\Scripts\activate`
  - `pip install -r backend\requirements.txt`
  - `python backend\scripts\inspect_dataset.py`
  - `python backend\scripts\generate_demo.py`
  - `pytest backend\tests -q`
  - `uvicorn backend.app.main:app --reload`
- Frontend:
  - `cd frontend`
  - `npm install`
  - `copy .env.example .env.local`
  - `npm run dev`

## Demo guide reference
- See `docs/DEMO_GUIDE.md`
