import pytest
from backend.app.schemas.finpulse import FinPulseFinancials
from backend.app.services.dimensions import all_dimensions, liquidity_health, debt_capacity
from backend.app.services.finpulse_score import finpulse_score, band
from backend.app.services.confidence import data_confidence
from backend.app.services.counterfactual import simulate
from backend.app.services.credit_readiness import credit_readiness

def firm(**kw):
    base = dict(msme_id="T1", cash_inflows=100, cash_outflows=90, monthly_revenue=100,
                revenue_growth_rate=.01, revenue_volatility=.05, liquidity_ratio=1.2,
                cash_reserve=100, operating_expenses=80, debt_service_ratio=.2,
                repayment_consistency=.9, gst_filing_consistency=.95,
                employee_growth_rate=.01, provenance="synthetic_demo")
    base.update(kw); return FinPulseFinancials(**base)

def test_dimensions_bounded():
    for d in all_dimensions(firm()).values():
        assert 0 <= d["score"] <= 100

def test_more_reserve_not_worse_liquidity():
    a, b = firm(cash_reserve=50), firm(cash_reserve=500)
    assert liquidity_health(b)["score"] >= liquidity_health(a)["score"]

def test_less_debt_not_worse_capacity():
    assert debt_capacity(firm(debt_service_ratio=.1))["score"] >= \
           debt_capacity(firm(debt_service_ratio=.5))["score"]

def test_finpulse_bounds_and_bands():
    dims = all_dimensions(firm())
    s = finpulse_score(dims, 0.2, 0.1)
    assert 0 <= s["finpulse_score"] <= 100
    assert band(90) == "Excellent" and band(30) == "Critical"

def test_higher_ml_risk_never_improves_score():
    dims = all_dimensions(firm())
    assert finpulse_score(dims, 0.9, 0.1)["finpulse_score"] <= \
           finpulse_score(dims, 0.1, 0.1)["finpulse_score"]

def test_missing_data_not_critical_but_low_confidence():
    sparse = FinPulseFinancials(msme_id="S", provenance="public_dataset")
    dims = all_dimensions(sparse)
    s = finpulse_score(dims, None, None)
    conf = data_confidence(sparse)
    assert s["band"] != "Critical"
    assert "Human Review" in conf["confidence_status"]

def test_counterfactual_uses_real_engine():
    r = simulate(firm(), {"cash_reserve": 400.0})
    assert "not a guarantee" in r["disclaimer"]
    assert r["score_change"] == round(r["simulated_score"] - r["current_score"], 1)

def test_no_loan_approved_ever():
    dims = all_dimensions(firm())
    s = finpulse_score(dims, 0.1, 0.05)
    conf = data_confidence(firm(), history_months=12)
    out = credit_readiness(s, dims, conf)
    assert "Loan Approved" not in str(out)

def test_low_confidence_triggers_review():
    sparse = FinPulseFinancials(msme_id="S2", provenance="public_dataset")
    dims = all_dimensions(sparse)
    s = finpulse_score(dims, None, None)
    out = credit_readiness(s, dims, data_confidence(sparse))
    assert out["credit_readiness"] == "Review Required"

# Additional tests to include (same pattern): target-missing removal, duplicate handling,
# leakage audit assertions on Decision_Loan_Approval, model artifact load + prob in [0,1],
# probability direction on a known distress-like record, twin deterioration/recovery/stable
# detection on synthetic histories, anomaly wording "Unusual Financial Pattern".