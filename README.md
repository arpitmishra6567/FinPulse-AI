# FinPulse AI

**Explainable Financial Health Intelligence for credit-invisible MSMEs**

FinPulse AI is an IDBI Innovate 2026 hackathon prototype that turns standardized MSME financial signals into a transparent financial-health identity. It combines six interpretable dimensions, temporal trend analysis, anomaly review signals, data-confidence reporting, indicative credit readiness, and counterfactual score simulation.

> Decision support only. FinPulse AI does not approve loans, claim fraud detection, or imply IDBI endorsement.

## What makes FinPulse different

- **Six explainable health dimensions:** cash-flow stability, liquidity resilience, revenue consistency, payment discipline, debt capacity, and business stability.
- **Temporal Financial Digital Twin:** re-scores 12 months of financial history and surfaces deterioration, recovery, and change points.
- **Honest ML applicability:** the stored public-survey model is not applied to incompatible synthetic demo cards. Demo records expose `risk_probability = null` and use the documented scoring fallback.
- **Data confidence stays separate:** missing evidence affects confidence rather than silently forcing a high-risk verdict.
- **Counterfactual simulation:** users can change supported financial variables and re-run the real scoring engine.
- **Responsible terminology:** unusual patterns are review signals, not fraud accusations.

## Architecture

```text
Public / synthetic / future sandbox adapters
                    |
          FinPulseFinancials schema
                    |
          FinPulseOrchestrator
                    |
  Six dimensions + score + confidence
  + anomaly + temporal twin + simulation
                    |
             FastAPI REST API
                    |
        Next.js + TypeScript frontend
```

**Architecture principle:** swap the connector, not the intelligence engine.

## Tech stack

**Backend:** Python, FastAPI, Pydantic, SQLAlchemy, pandas, NumPy, scikit-learn  
**Frontend:** Next.js 14, React 18, TypeScript, Tailwind CSS, Recharts, Lucide  
**ML:** Logistic Regression artifact, Isolation Forest anomaly signals  
**Validation:** Pytest, ESLint, TypeScript compiler, Next.js production build

## Verified status

The included `VERIFICATION_REPORT.md` records the verified Phase 2 checks:

- 20 backend tests passed
- 12 required API endpoint probes passed
- negative API validation checks passed
- scoring and responsible-AI semantic checks passed
- CORS verification passed
- frontend lint passed
- TypeScript validation passed
- Next.js production build passed
- all seven required frontend routes returned HTTP 200

The test bundle contains 20 tests, not 24. Browser visual click-through was not available in the verification environment; API-backed integration and HTTP route verification were completed instead.

## Repository structure

```text
FinPulse-AI/
├── backend/
│   ├── app/                  # FastAPI API, schemas, services, scoring orchestration
│   ├── data/                 # public survey + deterministic synthetic demo data
│   ├── ml/                   # training/inference code and model metadata
│   ├── scripts/              # dataset inspection and demo generation
│   ├── tests/                # backend integration tests
│   ├── requirements.txt      # full development/training dependencies
│   └── requirements-runtime.txt
├── frontend/                 # Next.js App Router application
├── docs/                     # API, architecture, demo and responsible-AI docs
├── render.yaml               # Render backend Blueprint
├── VERIFICATION_REPORT.md
└── README.md
```

## Run locally

### Backend — Windows PowerShell

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
pip install -r backend\requirements.txt
python backend\scripts\inspect_dataset.py
python backend\scripts\generate_demo.py
pytest backend\tests -q
uvicorn backend.app.main:app --reload
```

Backend: `http://127.0.0.1:8000`  
Swagger: `http://127.0.0.1:8000/docs`

Model training is optional. The API can run without retraining:

```powershell
python backend\ml\training\train.py
```

### Frontend

```powershell
cd frontend
npm install
Copy-Item .env.example .env.local
npm run dev
```

Frontend: `http://localhost:3000`

## Free deployment

Recommended deployment: **one public GitHub monorepo, Render for FastAPI, Vercel for Next.js**.

### 1. Push to GitHub

Create an empty repository named `FinPulse-AI`, then from this repository root:

```bash
git init
git branch -M main
git add .
git commit -m "feat: release FinPulse AI verified prototype"
git remote add origin https://github.com/YOUR_USERNAME/FinPulse-AI.git
git push -u origin main
```

### 2. Deploy the backend on Render

Connect the GitHub repository to Render. You can use the root `render.yaml` Blueprint, or configure a Web Service manually:

```text
Build Command: pip install -r backend/requirements-runtime.txt
Start Command: uvicorn backend.app.main:app --host 0.0.0.0 --port $PORT
Health Check Path: /health
```

Set:

```text
APP_ENV=production
CORS_ORIGINS=https://YOUR-PROJECT.vercel.app
```

After deployment, verify:

```text
https://YOUR-RENDER-SERVICE.onrender.com/health
https://YOUR-RENDER-SERVICE.onrender.com/docs
```

### 3. Deploy the frontend on Vercel

Import the same GitHub repository and set the **Root Directory** to `frontend`.

Add the environment variable:

```text
NEXT_PUBLIC_API_URL=https://YOUR-RENDER-SERVICE.onrender.com
```

Deploy the frontend. Copy the exact production Vercel URL, update `CORS_ORIGINS` on Render to that exact origin, and redeploy/restart the backend if required.

### 4. Final smoke test

Open the deployed frontend and verify this flow:

```text
Dashboard
→ MSME Portfolio
→ DEMO-001 Health Card
→ Temporal Twin
→ Explainability
→ Improve My Score
→ Transparency
```

Before a live demo on a sleeping free backend, open the backend `/health` endpoint first and wait for it to respond.

## API

Interactive OpenAPI documentation is available at `/docs`. Key routes include:

- `GET /health`
- `GET /api/v1/status`
- `GET /api/v1/msmes`
- `GET /api/v1/msmes/{id}/health-card`
- `GET /api/v1/msmes/{id}/twin`
- `GET /api/v1/msmes/{id}/explanation`
- `GET /api/v1/msmes/{id}/simulate/current`
- `POST /api/v1/msmes/{id}/simulate`
- `GET /api/v1/analytics/portfolio`
- model, scoring, and data-source metadata endpoints

See `docs/API.md` for the complete contract.

## Data and model transparency

The public dataset is survey-based and is not IDBI customer data. The demo portfolio contains 100 deterministic `synthetic_demo` MSMEs. GST/UPI/EPFO-style signals in the demo are synthetic.

The stored Logistic Regression artifact was trained on raw public-survey features. Those features are incompatible with the standardized demo financial schema, so the trained model is **not applied to demo health cards**. FinPulse exposes this limitation and uses the documented fallback rather than fabricating a prediction.

See `docs/RESPONSIBLE_AI.md` and the in-app Transparency page.

## Limitations

- Hackathon prototype, not a production banking system
- No real IDBI customer data or live IDBI API
- No automated loan approval
- No fraud-detection claim
- No authentication/RBAC or production audit trail
- Demo portfolio is synthetic and deterministic
- Browser visual E2E testing remains a future validation step

## License and use

No IDBI endorsement is implied. Review dataset and competition terms before commercial reuse. Add a repository license only after confirming the rights for every included dataset and artifact.
