import json, pathlib, joblib
import pandas as pd

ART = pathlib.Path(__file__).resolve().parents[1] / "artifacts"

class InferenceService:
    def __init__(self):
        self.model, self.meta, self.status = None, {}, "demo_fallback"
        try:
            self.model = joblib.load(ART / "model.joblib")
            self.meta = json.loads((ART / "model_metadata.json").read_text())
            self.status = self.meta.get("model_status", "trained_model")
        except Exception:
            pass  # app must still start
    @property
    def model_name(self): return self.meta.get("model_name", "none")
    def risk_probability(self, raw_features: dict) -> dict:
        if self.model is None:
            return {"risk_probability": 0.5, "model_status": "demo_fallback",
                    "note": "No trained model loaded — neutral fallback, NOT a prediction."}
        schema = json.loads((ART / "feature_schema.json").read_text())
        cols = schema["numerical"] + schema["categorical"]
        X = pd.DataFrame([{c: raw_features.get(c) for c in cols}])
        proba = self.model.predict_proba(X)[0]
        idx = self.meta["positive_probability_index"]
        return {"risk_probability": float(proba[idx]),
                "model_status": self.status, "model_name": self.model_name}