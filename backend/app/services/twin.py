"""Temporal Financial Digital Twin — real monthly re-scoring, transparent change logic."""
from backend.app.schemas.finpulse import FinPulseFinancials
from backend.app.services.dimensions import all_dimensions
from backend.app.services.finpulse_score import finpulse_score

def build_twin(history: list[dict]) -> dict:
    scores = []
    for m in history:
        f = FinPulseFinancials(**{k: v for k, v in m.items()
                                  if k in FinPulseFinancials.model_fields})
        dims = all_dimensions(f)
        scores.append(finpulse_score(dims, None, None)["finpulse_score"])
    def delta(n): return round(scores[-1] - scores[-1 - n], 1) if len(scores) > n else None
    d1, d3 = delta(1), delta(3)
    six = scores[-6:] if len(scores) >= 6 else scores
    slope = round((six[-1] - six[0]) / max(len(six) - 1, 1), 2)
    monthly_moves = [scores[i+1] - scores[i] for i in range(len(scores)-1)]
    sudden = any(m <= -10 for m in monthly_moves[-3:])
    if sudden: status = "sudden_deterioration"
    elif slope <= -1.5: status = "gradual_deterioration"
    elif slope >= 1.5 and min(six) < six[-1] - 5: status = "financial_recovery"
    elif abs(slope) < 1.5 and max(map(abs, monthly_moves or [0])) < 8: status = "stable"
    else: status = "abnormal_score_movement"
    change_points = [i for i, m in enumerate(monthly_moves) if abs(m) >= 10]
    return {"score_history": scores, "change_1m": d1, "change_3m": d3,
            "trend_6m_slope": slope,
            "deterioration_velocity": round(min(monthly_moves or [0]), 1),
            "recovery_velocity": round(max(monthly_moves or [0]), 1),
            "trend_status": status,
            "trend_summary": f"6-month slope {slope:+.2f} pts/month; latest 1m change {d1}",
            "change_points": change_points,
            "detected_start_period": (change_points[0] if change_points else None),
            "affected_dimensions": "computed per-month via dimension engines (transparent logic)"}