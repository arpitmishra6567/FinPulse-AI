"""Indicative decision-support band. NEVER outputs 'Loan Approved'."""
def credit_readiness(finpulse, dims, confidence) -> dict:
    if confidence["confidence_score"] < 45:
        state, why = "Review Required", "Low data confidence — human review preferred."
    else:
        cf, dc, lq = (dims[k]["score"] for k in
                      ("cash_flow_health", "debt_capacity", "liquidity_health"))
        s = finpulse["finpulse_score"]
        if s >= 75 and min(cf, dc, lq) >= 60: state, why = "Strong", "Broad-based financial health."
        elif s >= 55 and min(cf, dc, lq) >= 45: state, why = "Moderate", "Adequate health with monitorable gaps."
        elif s >= 40: state, why = "Limited", "Material weaknesses in core dimensions."
        else: state, why = "Review Required", "Weak indicators — structured review recommended."
    return {"credit_readiness": state, "rationale": why,
            "disclaimer": "Indicative assessment for decision support. "
                          "FinPulse AI does not replace the credit decision-maker."}