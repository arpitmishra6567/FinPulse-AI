"""Six transparent dimension engines. Missing data -> neutral score + confidence penalty
(handled by confidence engine), NOT automatic critical risk."""
from backend.app.schemas.finpulse import FinPulseFinancials

NEUTRAL = 50.0
def _clamp(x): return max(0.0, min(100.0, x))

def cash_flow_health(f: FinPulseFinancials) -> dict:
    pos, risk = [], []
    if f.cash_inflows is None or f.cash_outflows is None:
        return _pack(NEUTRAL, pos, ["Cash-flow data unavailable"], neutral=True)
    ratio = f.cash_inflows / max(f.cash_outflows, 1)
    score = _clamp(50 + (ratio - 1) * 120)
    if f.upi_inflow_stability is not None:
        score = _clamp(score + (f.upi_inflow_stability - .5) * 20)
        if f.upi_inflow_stability > .7: pos.append("Stable digital (UPI-style) inflows [synthetic_demo]")
    if ratio >= 1.1: pos.append("Inflows comfortably exceed outflows")
    if ratio < .95: risk.append("Cash outflows exceed inflows")
    return _pack(score, pos, risk)

def revenue_stability(f):
    pos, risk = [], []
    if f.revenue_growth_rate is None and f.revenue_volatility is None:
        return _pack(NEUTRAL, pos, ["Revenue trend data unavailable"], neutral=True)
    score = 50 + (f.revenue_growth_rate or 0) * 400 - (f.revenue_volatility or .05) * 150
    if (f.revenue_growth_rate or 0) > .01: pos.append("Positive revenue growth")
    if (f.revenue_growth_rate or 0) < -.02: risk.append("Revenue deterioration")
    if (f.revenue_volatility or 0) > .12: risk.append("High revenue volatility")
    return _pack(_clamp(score), pos, risk)

def liquidity_health(f):
    pos, risk = [], []
    if f.liquidity_ratio is None:
        return _pack(NEUTRAL, pos, ["Liquidity data unavailable"], neutral=True)
    score = _clamp(f.liquidity_ratio / 2.0 * 100)          # ratio 2.0 -> 100
    if f.cash_reserve and f.operating_expenses:
        runway = f.cash_reserve / max(f.operating_expenses, 1)
        score = _clamp(0.7 * score + 0.3 * _clamp(runway * 40))
        if runway >= 1.5: pos.append("Healthy cash-reserve runway")
    if f.liquidity_ratio >= 1.5: pos.append("Strong liquidity ratio")
    if f.liquidity_ratio < .8: risk.append("Thin liquidity buffer")
    return _pack(score, pos, risk)

def compliance_health(f):
    pos, risk = [], []
    if f.gst_filing_consistency is None:
        return _pack(NEUTRAL, pos, ["Compliance signals unavailable"], neutral=True)
    score = _clamp(f.gst_filing_consistency * 100)
    if f.gst_filing_consistency > .9: pos.append("Consistent GST-style filing [synthetic_demo]")
    if f.gst_filing_consistency < .6: risk.append("Irregular compliance filings")
    return _pack(score, pos, risk)

def employment_stability(f):
    pos, risk = [], []
    if f.employee_growth_rate is None and f.epfo_contribution_consistency is None:
        return _pack(NEUTRAL, pos, ["Employment signals unavailable"], neutral=True)
    score = 50 + (f.employee_growth_rate or 0) * 300
    if f.epfo_contribution_consistency is not None:
        score = 0.6 * score + 0.4 * f.epfo_contribution_consistency * 100
        if f.epfo_contribution_consistency > .85:
            pos.append("Consistent EPFO-style contributions [synthetic_demo]")
    g, r = f.employee_growth_rate or 0, f.revenue_growth_rate or 0
    if g > 0 and r > 0: pos.append("Expansion: employee and revenue growth aligned")
    if g > 0 and r < -.02: risk.append("Employee growth amid falling revenue (operating pressure)")
    return _pack(_clamp(score), pos, risk)

def debt_capacity(f):
    pos, risk = [], []
    if f.debt_service_ratio is None:
        return _pack(NEUTRAL, pos, ["Debt data unavailable"], neutral=True)
    score = _clamp(100 - f.debt_service_ratio * 180)       # DSR 0 ->100, 0.55->~0
    if f.repayment_consistency is not None:
        score = _clamp(0.75 * score + 0.25 * f.repayment_consistency * 100)
        if f.repayment_consistency > .85: pos.append("Consistent repayment behaviour")
    if f.debt_service_ratio < .2: pos.append("Low debt-service burden")
    if f.debt_service_ratio > .45: risk.append("Elevated debt-service pressure")
    return _pack(score, pos, risk)

def _pack(score, pos, risk, neutral=False):
    status = ("No Data — Neutral" if neutral else
              "Healthy" if score >= 70 else "Adequate" if score >= 50 else
              "Stressed" if score >= 35 else "Weak")
    return {"score": round(_clamp(score), 1), "status": status, "trend": "n/a",
            "positive_evidence": pos, "risk_signals": risk, "neutral_fallback": neutral}

def all_dimensions(f: FinPulseFinancials) -> dict:
    return {"cash_flow_health": cash_flow_health(f), "revenue_stability": revenue_stability(f),
            "liquidity_health": liquidity_health(f), "compliance_health": compliance_health(f),
            "employment_stability": employment_stability(f), "debt_capacity": debt_capacity(f)}