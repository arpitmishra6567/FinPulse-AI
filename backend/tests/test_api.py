"""Phase 2 integration tests. Demo data is generated once (deterministic, seed 42)
if missing. No model retraining occurs inside API tests."""
import pytest
from fastapi.testclient import TestClient

from backend.app.services.orchestrator import DEMO_JSON, FinPulseOrchestrator


@pytest.fixture(scope="session", autouse=True)
def ensure_demo():
    if not DEMO_JSON.exists():
        from backend.scripts.generate_demo import main as gen
        gen()
    FinPulseOrchestrator.reset()


@pytest.fixture(scope="session")
def client():
    from backend.app.main import app
    return TestClient(app)


def test_health_and_status(client):
    assert client.get("/health").status_code == 200
    r = client.get("/api/v1/status")
    assert r.status_code == 200
    assert r.json()["model_application_status_for_demo"] in (
        "applied", "not_applicable_to_demo_schema", "demo_fallback", "artifact_unavailable")


def test_portfolio_pagination_and_shape(client):
    r = client.get("/api/v1/msmes?page=1&page_size=10").json()
    assert r["total"] >= 50 and len(r["items"]) == 10
    row = r["items"][0]
    for k in ("msme_id", "band", "confidence_status", "trend_status",
              "credit_readiness", "anomaly_status", "provenance"):
        assert k in row
    assert row["provenance"] == "synthetic_demo"


def test_portfolio_filters(client):
    r = client.get("/api/v1/msmes?health_band=Critical&page_size=100").json()
    assert all(i["band"] == "Critical" for i in r["items"])
    r2 = client.get("/api/v1/msmes?sort_by=finpulse_score&sort_order=asc&page_size=100").json()
    scores = [i["finpulse_score"] for i in r2["items"]]
    assert scores == sorted(scores)


def test_unknown_msme_404(client):
    for path in ("", "/health-card", "/twin", "/explanation"):
        assert client.get(f"/api/v1/msmes/NOPE-999{path}").status_code == 404
    assert client.post("/api/v1/msmes/NOPE-999/simulate",
                       json={"cash_reserve": 100}).status_code == 404


def test_health_card_contract(client):
    mid = client.get("/api/v1/msmes?page_size=1").json()["items"][0]["msme_id"]
    hc = client.get(f"/api/v1/msmes/{mid}/health-card").json()
    assert 0 <= hc["finpulse_score"] <= 100
    assert len(hc["dimensions"]) == 6
    for d in hc["dimensions"].values():
        assert 0 <= d["score"] <= 100
    assert hc["weights"] == {"dimensions": 0.65, "ml_risk": 0.25, "anomaly": 0.10}
    assert "confidence_score" in hc["confidence"]          # separate from score
    assert hc["model"]["model_application_status"] in (
        "applied", "not_applicable_to_demo_schema", "demo_fallback", "artifact_unavailable")
    if hc["model"]["model_application_status"] != "applied":
        assert hc["model"]["risk_probability"] is None     # never fake a prediction


def test_twin_is_real_monthly_rescoring(client):
    mid = client.get("/api/v1/msmes?page_size=1").json()["items"][0]["msme_id"]
    tw = client.get(f"/api/v1/msmes/{mid}/twin").json()
    assert len(tw["score_history"]) == 12
    assert all(0 <= s <= 100 for s in tw["score_history"])
    assert tw["trend_status"] in ("stable", "gradual_deterioration", "financial_recovery",
                                  "sudden_deterioration", "abnormal_score_movement")


def test_explanation_honest_fallback(client):
    mid = client.get("/api/v1/msmes?page_size=1").json()["items"][0]["msme_id"]
    ex = client.get(f"/api/v1/msmes/{mid}/explanation").json()
    assert ex["explanation_mode"] in ("shap_and_rules", "rules_fallback")
    if ex["explanation_mode"] == "rules_fallback":
        assert ex["ml_factors"] == []                       # never fabricated SHAP
    assert len(ex["financial_health_signals"]) == 6


def test_simulation_validation_and_engine(client):
    mid = client.get("/api/v1/msmes?page_size=1").json()["items"][0]["msme_id"]
    assert client.post(f"/api/v1/msmes/{mid}/simulate", json={}).status_code == 422
    assert client.post(f"/api/v1/msmes/{mid}/simulate",
                       json={"receivable_days": 9999}).status_code == 422
    r = client.post(f"/api/v1/msmes/{mid}/simulate",
                    json={"receivable_days": 20, "cash_reserve": 500000}).json()
    assert r["score_change"] == round(r["simulated_score"] - r["current_score"], 1)
    assert "not a guarantee" in r["disclaimer"]


def test_analytics_are_calculated(client):
    a = client.get("/api/v1/analytics/portfolio").json()
    assert a["total_msmes"] == sum(a["band_distribution"].values())
    assert 0 <= a["average_finpulse_score"] <= 100
    assert isinstance(a["attention_signals"], list)


def test_metadata_endpoints(client):
    s = client.get("/api/v1/metadata/scoring").json()
    assert abs(sum(s["dimension_weights"].values()) - 1.0) < 1e-9
    assert client.get("/api/v1/metadata/model").status_code == 200
    ds = client.get("/api/v1/metadata/data-sources").json()
    assert "synthetic_demo" in ds["provenance_definitions"]


def test_responsible_terminology(client):
    mid = client.get("/api/v1/msmes?page_size=1").json()["items"][0]["msme_id"]
    blob = str(client.get(f"/api/v1/msmes/{mid}/health-card").json())
    blob += str(client.get("/api/v1/analytics/portfolio").json())
    assert "Loan Approved" not in blob
    assert "Fraud Detected" not in blob