"""SHAP for ML Factors; transparent rules for Financial Health Signals; honest fallback."""
def explain(inference_service, raw_features: dict, dimensions: dict) -> dict:
    health_signals = [{ "dimension": k, "score": v["score"],
                        "positive": v["positive_evidence"], "risks": v["risk_signals"]}
                      for k, v in dimensions.items()]
    ml_factors, mode = [], "rules_fallback"
    try:
        import shap, pandas as pd, json, pathlib
        model = inference_service.model
        if model is None: raise RuntimeError("no model")
        pre, clf = model.named_steps["pre"], model.named_steps["clf"]
        ART = pathlib.Path(__file__).resolve().parents[2] / "ml/artifacts"
        schema = json.loads((ART / "feature_schema.json").read_text())
        X = pd.DataFrame([{c: raw_features.get(c) for c in
                           schema["numerical"] + schema["categorical"]}])
        Xt = pre.transform(X)
        expl = shap.Explainer(clf, Xt) if hasattr(clf, "predict_proba") else None
        sv = expl(Xt)
        names = pre.get_feature_names_out()
        vals = sv.values[0] if sv.values.ndim == 2 else sv.values[0][:, -1]
        top = sorted(zip(names, vals), key=lambda t: -abs(t[1]))[:8]
        ml_factors = [{"feature": n, "shap_value": round(float(v), 4)} for n, v in top]
        mode = "shap_and_rules"
    except Exception:
        mode = "rules_fallback"
    return {"explanation_mode": mode, "ml_factors": ml_factors,
            "financial_health_signals": health_signals}