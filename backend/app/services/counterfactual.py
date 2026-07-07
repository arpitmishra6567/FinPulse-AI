"""Improve My Score — re-runs the REAL scoring engine; never adds arbitrary points."""
from copy import deepcopy
from backend.app.services.dimensions import all_dimensions
from backend.app.services.finpulse_score import finpulse_score

ALLOWED = {"receivable_days": (5, 180), "cash_reserve": (0, 1e9),
           "customer_concentration": (0.0, 1.0), "debt_service_ratio": (0.0, 1.5)}

def simulate(current, changes: dict, risk_prob=None, anomaly=None) -> dict:
    for k, v in changes.items():
        if k not in ALLOWED: raise ValueError(f"Field not simulatable: {k}")
        lo, hi = ALLOWED[k]
        if not (lo <= v <= hi): raise ValueError(f"{k}={v} outside [{lo},{hi}]")
    base_dims = all_dimensions(current)
    base = finpulse_score(base_dims, risk_prob, anomaly)
    sim = deepcopy(current)
    for k, v in changes.items(): setattr(sim, k, v)
    sim_dims = all_dimensions(sim)
    new = finpulse_score(sim_dims, risk_prob, anomaly)
    return {"current_score": base["finpulse_score"], "simulated_score": new["finpulse_score"],
            "score_change": round(new["finpulse_score"] - base["finpulse_score"], 1),
            "dimension_changes": {k: round(sim_dims[k]["score"] - base_dims[k]["score"], 1)
                                  for k in sim_dims},
            "improvement_insights": [f"{k} -> {v}" for k, v in changes.items()],
            "disclaimer": "Simulation only — not a guarantee of credit approval."}