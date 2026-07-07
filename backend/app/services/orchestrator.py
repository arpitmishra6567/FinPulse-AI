"""FinPulseOrchestrator — central Phase 2 orchestration.

Loads the deterministic synthetic_demo portfolio ONCE at startup, fits the
Isolation Forest on the demo population ONCE, and computes every Phase 1
intelligence output (six dimensions, FinPulse Score, Data Confidence,
Temporal Twin, anomaly status, credit readiness) per MSME. Routers never
duplicate scoring logic and NOTHING is retrained inside an API request.

CRITICAL ML CONSTRAINT (honoured):
The Phase 1 trained model consumes RAW public-survey features (SME_Age,
Literacy_*, Risk_*, ...). Demo Financial Health Cards carry STANDARDIZED
financial features (cash_inflows, debt_service_ratio, ...). These schemas are
incompatible, so we NEVER fake a trained prediction for demo cards:
risk_probability = None and the documented score fallback applies
(ml_component := dimension composite). model_application_status is exposed
honestly on every card.
"""
import json
import pathlib
import threading

from backend.app.schemas.finpulse import FinPulseFinancials
from backend.app.services.dimensions import all_dimensions
from backend.app.services.finpulse_score import finpulse_score, DIM_WEIGHTS, BANDS
from backend.app.services.confidence import data_confidence
from backend.app.services.anomaly import fit_anomaly_model, anomaly_assess
from backend.app.services.twin import build_twin
from backend.app.services.counterfactual import simulate, ALLOWED
from backend.app.services.credit_readiness import credit_readiness
from backend.ml.inference.service import InferenceService

BASE = pathlib.Path(__file__).resolve().parents[2]
DEMO_JSON = BASE / "data" / "demo" / "demo_msmes.json"

DEMO_GUIDANCE = ("Demo portfolio not found. Generate the deterministic synthetic_demo "
                 "portfolio first: python backend/scripts/generate_demo.py")

DISCLAIMERS = [
    "FinPulse AI is a decision-support prototype. It does not approve loans.",
    "An unusual financial pattern is a review signal, not proof of wrongdoing.",
    "Alternative signals (GST/UPI/EPFO-style) are synthetic_demo, not real bureau data.",
    "IDBI Innovate 2026 Prototype — no IDBI endorsement implied.",
]


class FinPulseOrchestrator:
    _instance = None
    _lock = threading.Lock()

    @classmethod
    def get(cls) -> "FinPulseOrchestrator":
        with cls._lock:
            if cls._instance is None:
                cls._instance = cls()
            return cls._instance

    @classmethod
    def reset(cls):
        with cls._lock:
            cls._instance = None

    # ------------------------------------------------------------------ init
    def __init__(self):
        self.inference = InferenceService()          # loaded once, cached
        self.records: dict[str, dict] = {}
        self.assessments: dict[str, dict] = {}
        self.anomaly_model = None
        self.demo_available = DEMO_JSON.exists()
        if self.demo_available:
            self._load()

    def _load(self):
        raw = json.loads(DEMO_JSON.read_text())
        for r in raw:
            self.records[r["msme_id"]] = r
        # Fit anomaly model ONCE on the deterministic population (never per request).
        self.anomaly_model = fit_anomaly_model([r["latest"] for r in raw])
        for mid, r in self.records.items():
            self.assessments[mid] = self._assess(r)

    # ------------------------------------------------------------ core logic
    @staticmethod
    def _fin(payload: dict) -> FinPulseFinancials:
        return FinPulseFinancials(**{k: v for k, v in payload.items()
                                     if k in FinPulseFinancials.model_fields})

    def model_application_status(self) -> str:
        if self.inference.model is None:
            return "artifact_unavailable"
        # Trained on raw survey schema; demo cards use standardized schema.
        return "not_applicable_to_demo_schema"

    def _assess(self, rec: dict) -> dict:
        latest, history = rec["latest"], rec["history"]
        f = self._fin(latest)
        dims = all_dimensions(f)
        anomaly = anomaly_assess(self.anomaly_model, latest)
        risk_probability = None  # honest: survey model not applicable to demo schema
        score = finpulse_score(dims, risk_probability, anomaly["anomaly_score"])
        conf = data_confidence(f, history_months=len(history))
        twin = build_twin(history)
        readiness = credit_readiness(score, dims, conf)
        return {"financials": f, "dims": dims, "anomaly": anomaly, "score": score,
                "confidence": conf, "twin": twin, "readiness": readiness,
                "risk_probability": risk_probability, "archetype": rec.get("archetype")}

    def _require(self, msme_id: str) -> dict:
        a = self.assessments.get(msme_id)
        if a is None:
            raise KeyError(msme_id)
        return a

    # ------------------------------------------------------------- summaries
    def summary(self, msme_id: str) -> dict:
        a = self._require(msme_id)
        f = a["financials"]
        return {
            "msme_id": msme_id,
            "business_name": f.business_name,
            "sector": f.sector,
            "finpulse_score": a["score"]["finpulse_score"],
            "band": a["score"]["band"],
            "confidence_score": a["confidence"]["confidence_score"],
            "confidence_status": a["confidence"]["confidence_status"],
            "trend_status": a["twin"]["trend_status"],
            "credit_readiness": a["readiness"]["credit_readiness"],
            "anomaly_status": a["anomaly"]["anomaly_status"],
            "latest_monthly_revenue": f.monthly_revenue,
            "provenance": f.provenance,
        }

    def list_msmes(self, *, search=None, sector=None, health_band=None,
                   trend_status=None, credit_readiness_f=None, confidence_status=None,
                   anomaly_status=None, sort_by="finpulse_score", sort_order="desc",
                   page=1, page_size=20) -> dict:
        items = [self.summary(mid) for mid in self.records]
        if search:
            s = search.lower()
            items = [i for i in items if s in (i["business_name"] or "").lower()
                     or s in i["msme_id"].lower()]
        if sector:
            items = [i for i in items if i["sector"] == sector]
        if health_band:
            items = [i for i in items if i["band"] == health_band]
        if trend_status:
            items = [i for i in items if i["trend_status"] == trend_status]
        if credit_readiness_f:
            items = [i for i in items if i["credit_readiness"] == credit_readiness_f]
        if confidence_status:
            items = [i for i in items
                     if i["confidence_status"].startswith(confidence_status)]
        if anomaly_status:
            items = [i for i in items if i["anomaly_status"] == anomaly_status]
        valid_sort = {"finpulse_score", "confidence_score", "business_name",
                      "msme_id", "latest_monthly_revenue", "sector"}
        key = sort_by if sort_by in valid_sort else "finpulse_score"
        items.sort(key=lambda i: (i[key] is None, i[key]),
                   reverse=(sort_order != "asc"))
        total = len(items)
        page = max(1, page)
        start = (page - 1) * page_size
        return {"items": items[start:start + page_size], "total": total,
                "page": page, "page_size": page_size,
                "total_pages": max(1, -(-total // page_size)),
                "demo_available": self.demo_available}

    # ------------------------------------------------------------ full views
    def health_card(self, msme_id: str) -> dict:
        a = self._require(msme_id)
        f = a["financials"]
        return {
            "identity": {"msme_id": msme_id, "business_name": f.business_name,
                         "sector": f.sector, "business_age_years": f.business_age_years,
                         "provenance": f.provenance},
            "finpulse_score": a["score"]["finpulse_score"],
            "band": a["score"]["band"],
            "components": a["score"]["components"],
            "weights": a["score"]["weights"],
            "dimensions": a["dims"],
            "dimension_weights": DIM_WEIGHTS,
            "confidence": a["confidence"],
            "credit_readiness": a["readiness"],
            "anomaly": a["anomaly"],
            "trend": {k: a["twin"][k] for k in
                      ("trend_status", "change_1m", "change_3m", "trend_6m_slope")},
            "model": {"model_application_status": self.model_application_status(),
                      "model_status": self.inference.status,
                      "model_name": self.inference.model_name,
                      "risk_probability": a["risk_probability"],
                      "note": "risk_probability is None: the survey-trained model does not "
                              "apply to the standardized demo schema; the documented score "
                              "fallback (ml_component = dimension composite) is used."},
            "disclaimers": DISCLAIMERS,
        }

    def twin(self, msme_id: str) -> dict:
        a = self._require(msme_id)
        return {"msme_id": msme_id, **a["twin"],
                "note": "Monthly scores are produced by re-running the real Phase 1 "
                        "dimension + scoring engines per month. Transparent logic, "
                        "not deep learning."}

    def explanation(self, msme_id: str) -> dict:
        a = self._require(msme_id)
        signals = [{"dimension": k, "score": v["score"], "status": v["status"],
                    "positive": v["positive_evidence"], "risks": v["risk_signals"],
                    "neutral_fallback": v["neutral_fallback"]}
                   for k, v in a["dims"].items()]
        return {"msme_id": msme_id,
                "explanation_mode": "rules_fallback",
                "model_application_status": self.model_application_status(),
                "ml_factors": [],
                "ml_factors_note": ("Model-level SHAP factors are unavailable for this "
                                    "record. The trained model uses raw public-survey "
                                    "features absent from the standardized demo schema. "
                                    "Transparent financial-health rules are shown below."),
                "financial_health_signals": signals,
                "responsible_ai_note": ("Explanations describe financial-health evidence, "
                                        "not creditworthiness verdicts. Human review is "
                                        "part of the intended workflow.")}

    def run_simulation(self, msme_id: str, changes: dict) -> dict:
        a = self._require(msme_id)
        result = simulate(a["financials"], changes,
                          risk_prob=a["risk_probability"],
                          anomaly=a["anomaly"]["anomaly_score"])
        result["msme_id"] = msme_id
        result["current_values"] = {k: getattr(a["financials"], k) for k in ALLOWED}
        result["allowed_fields"] = {k: list(v) for k, v in ALLOWED.items()}
        return result

    # -------------------------------------------------------------- analytics
    def portfolio_analytics(self) -> dict:
        summaries = [self.summary(mid) for mid in self.records]
        n = len(summaries)

        def dist(key):
            out: dict[str, int] = {}
            for s in summaries:
                out[s[key]] = out.get(s[key], 0) + 1
            return out

        attention = []
        for s in summaries:
            reasons = []
            if s["band"] in ("Critical", "Vulnerable"):
                reasons.append(f"{s['band']} health band")
            if s["trend_status"] == "sudden_deterioration":
                reasons.append("Sudden deterioration in Temporal Twin")
            elif s["trend_status"] == "gradual_deterioration":
                reasons.append("Gradual deterioration trend")
            if s["anomaly_status"] == "Unusual Financial Pattern":
                reasons.append("Unusual financial pattern — review signal")
            if s["confidence_status"].startswith("Limited"):
                reasons.append("Limited evidence — human review recommended")
            if reasons:
                attention.append({**{k: s[k] for k in
                                     ("msme_id", "business_name", "sector",
                                      "finpulse_score", "band")},
                                  "reasons": reasons})
        attention.sort(key=lambda x: (-len(x["reasons"]), x["finpulse_score"]))

        readiness = dist("credit_readiness")
        return {
            "total_msmes": n,
            "average_finpulse_score": round(sum(s["finpulse_score"] for s in summaries) / n, 1) if n else None,
            "average_confidence_score": round(sum(s["confidence_score"] for s in summaries) / n, 1) if n else None,
            "band_distribution": dist("band"),
            "credit_readiness_distribution": readiness,
            "strong_or_moderate_readiness_count": readiness.get("Strong", 0) + readiness.get("Moderate", 0),
            "trend_distribution": dist("trend_status"),
            "sector_distribution": dist("sector"),
            "unusual_pattern_count": sum(1 for s in summaries
                                         if s["anomaly_status"] == "Unusual Financial Pattern"),
            "low_confidence_count": sum(1 for s in summaries
                                        if s["confidence_status"].startswith("Limited")),
            "improving_count": sum(1 for s in summaries
                                   if s["trend_status"] in ("financial_recovery",)),
            "deteriorating_count": sum(1 for s in summaries if "deterioration" in s["trend_status"]),
            "attention_signals": attention[:12],
            "demo_available": self.demo_available,
        }

    # --------------------------------------------------------------- metadata
    def scoring_metadata(self) -> dict:
        return {
            "formula": ("Score = clamp(0.65 × Dimension Composite + 0.25 × 100 × "
                        "(1 − risk_probability) + 0.10 × 100 × (1 − anomaly_score), 0, 100)"),
            "fallbacks": {"risk_probability_none": "ml_component = dimension composite",
                          "anomaly_none": "anomaly_component = 100"},
            "dimension_weights": DIM_WEIGHTS,
            "bands": [{"min_score": t, "band": b} for t, b in BANDS],
            "data_confidence_note": ("Data Confidence measures evidence quality and is "
                                     "reported separately — never blended into the score."),
        }

    def model_metadata(self) -> dict:
        return {
            "model_status": self.inference.status,
            "model_name": self.inference.model_name,
            "metadata": self.inference.meta or None,
            "model_application_status_for_demo": self.model_application_status(),
            "application_limits": [
                "Trained on a public SME survey dataset (raw Likert/behavioural features).",
                "Not trained on IDBI customer data.",
                "Not applicable to the standardized demo financial schema; the score "
                "fallback is used for demo Financial Health Cards.",
                "Never treat the neutral 0.5 fallback as a trained prediction.",
            ],
        }

    @staticmethod
    def data_sources_metadata() -> dict:
        return {
            "provenance_definitions": {
                "public_dataset": "Public SME survey CSV (Finanical_data_sme.csv). Perception/"
                                  "survey data — not IDBI customer data.",
                "synthetic_demo": "Deterministic generated MSMEs with GST/UPI/EPFO-style "
                                  "signals. Clearly synthetic, seeded (reproducible).",
                "future_sandbox": "Interface stub only — pending sandbox access if shortlisted. "
                                  "No real IDBI endpoints are invented.",
            },
            "limitations": [
                "No IDBI customer data is used anywhere.",
                "No real IDBI API is called; FutureIDBISandboxAdapter is a stub.",
                "The public dataset is survey-based, not transactional.",
                "Alternative-data signals in demos are synthetic.",
                "FinPulse AI is decision support only — never automated loan approval.",
            ],
            "architecture_principle": "Swap the connector, not the intelligence engine.",
        }