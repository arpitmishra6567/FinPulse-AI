"""Data Confidence: evidence quality, NOT financial risk."""
CRITICAL = ["monthly_revenue", "cash_inflows", "cash_outflows", "liquidity_ratio",
            "debt_service_ratio", "cash_reserve"]
ALL_TRACKED = CRITICAL + ["revenue_growth_rate","receivable_days","customer_concentration",
    "gst_filing_consistency","upi_inflow_stability","epfo_contribution_consistency",
    "repayment_consistency","employee_growth_rate"]

def data_confidence(f, history_months: int = 0) -> dict:
    present = [k for k in ALL_TRACKED if getattr(f, k, None) is not None]
    completeness = len(present) / len(ALL_TRACKED)                       # 0..1
    crit = sum(getattr(f, k, None) is not None for k in CRITICAL) / len(CRITICAL)
    depth = min(history_months / 12, 1.0)
    sources = sum([f.provenance is not None,
                   f.gst_filing_consistency is not None,
                   f.upi_inflow_stability is not None,
                   f.epfo_contribution_consistency is not None]) / 4
    score = round(100 * (0.35*completeness + 0.30*crit + 0.20*depth + 0.15*sources), 1)
    status = ("High Confidence" if score >= 70 else "Moderate Confidence" if score >= 45
              else "Limited Evidence — Human Review Recommended")
    return {"confidence_score": score, "confidence_status": status,
            "coverage_details": {"fields_present": present, "history_months": history_months},
            "missing_critical_evidence": [k for k in CRITICAL if getattr(f, k, None) is None],
            "recommendation": ("Proceed with automated insight" if score >= 70 else
                               "Supplement data sources" if score >= 45 else
                               "Limited Evidence — Human Review Recommended")}