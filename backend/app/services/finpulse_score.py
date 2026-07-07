"""FinPulse Score = 0.65*DimComposite + 0.25*(100*(1-risk_prob)) + 0.10*(100*(1-anomaly)),
clamped 0-100. Data Confidence is reported separately, never blended in."""
DIM_WEIGHTS = {"cash_flow_health": .25, "revenue_stability": .20, "liquidity_health": .20,
               "compliance_health": .10, "employment_stability": .10, "debt_capacity": .15}
BANDS = [(85, "Excellent"), (70, "Good"), (55, "Watch"), (40, "Vulnerable"), (0, "Critical")]

def band(score): return next(b for t, b in BANDS if score >= t)

def finpulse_score(dimensions: dict, risk_probability: float | None,
                   anomaly_score: float | None) -> dict:
    dim = sum(dimensions[k]["score"] * w for k, w in DIM_WEIGHTS.items())
    ml = 100 * (1 - risk_probability) if risk_probability is not None else dim
    an = 100 * (1 - anomaly_score) if anomaly_score is not None else 100.0
    raw = 0.65 * dim + 0.25 * ml + 0.10 * an
    score = round(max(0.0, min(100.0, raw)), 1)
    return {"finpulse_score": score, "band": band(score),
            "components": {"dimension_composite": round(dim, 1),
                           "ml_component": round(ml, 1), "anomaly_component": round(an, 1)},
            "weights": {"dimensions": 0.65, "ml_risk": 0.25, "anomaly": 0.10}}