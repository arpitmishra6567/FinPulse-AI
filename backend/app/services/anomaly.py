"""Isolation Forest -> 'Unusual Financial Pattern' terminology only. Never 'fraud'."""
import numpy as np
from sklearn.ensemble import IsolationForest

FIELDS = ["monthly_revenue","cash_inflows","cash_outflows","cash_reserve",
          "liquidity_ratio","debt_service_ratio","revenue_growth_rate"]

def fit_anomaly_model(population: list[dict]) -> IsolationForest:
    X = np.array([[p.get(k) or 0 for k in FIELDS] for p in population])
    return IsolationForest(random_state=42, contamination=0.08).fit(X)

def anomaly_assess(model, record: dict) -> dict:
    x = np.array([[record.get(k) or 0 for k in FIELDS]])
    raw = float(model.score_samples(x)[0])                 # higher = more normal
    score = float(np.clip((0.0 - raw) / 0.5, 0, 1))        # 0 normal .. 1 unusual
    signals = []
    if (record.get("revenue_growth_rate") or 0) < -0.08: signals.append("Abnormal revenue movement")
    if record.get("cash_outflows") and record.get("cash_inflows") and \
       record["cash_outflows"] > 1.3 * record["cash_inflows"]:
        signals.append("Unusual cash outflow pattern")
    if (record.get("debt_service_ratio") or 0) > 0.5: signals.append("Debt-service stress")
    status = "Unusual Financial Pattern" if (score > 0.6 or signals) else "No Unusual Pattern Detected"
    return {"anomaly_score": round(score, 3), "anomaly_status": status,
            "detected_signals": signals,
            "note": "An unusual pattern is a review signal, not proof of wrongdoing."}