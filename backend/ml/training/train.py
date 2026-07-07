"""Cleaning, leakage audit, model comparison, selection, artifact persistence."""
import json, pathlib
from datetime import date
import numpy as np, pandas as pd, joblib
from sklearn.pipeline import Pipeline
from sklearn.compose import ColumnTransformer
from sklearn.impute import SimpleImputer
from sklearn.preprocessing import StandardScaler, OneHotEncoder
from sklearn.linear_model import LogisticRegression
from sklearn.ensemble import RandomForestClassifier
from sklearn.model_selection import train_test_split
from sklearn.metrics import (accuracy_score, roc_auc_score, average_precision_score,
                             precision_score, recall_score, f1_score, brier_score_loss,
                             confusion_matrix)

BASE = pathlib.Path(__file__).resolve().parents[2]
RAW = BASE / "data/raw/Finanical_data_sme.csv"
ART = BASE / "ml/artifacts"; EVAL = BASE / "ml/evaluation"; PROC = BASE / "data/processed"
TARGET = "Financial_Distress"
RANDOM_STATE = 42

# ---- Strict leakage / exclusion audit (semantic reasoning) ----
EXCLUSIONS = {
    "Decision_Loan_Approval": "Suspected downstream credit decision -> excluded by default (leakage policy).",
    "Has_Financial_Questions": "Constant value ('YES') for all rows -> zero variance, no signal.",
}

def leakage_audit(df: pd.DataFrame) -> dict:
    audit = []
    for col in df.columns:
        if col == TARGET:
            audit.append({"column_name": col, "decision": "target",
                          "reason": "Supervised label: 1 = financial distress."})
        elif col in EXCLUSIONS:
            audit.append({"column_name": col, "decision": "excluded", "reason": EXCLUSIONS[col]})
        else:
            audit.append({"column_name": col, "decision": "included",
                          "reason": "Pre-outcome self-reported financial capability/behaviour signal."})
    return {"target": TARGET, "audit": audit,
            "decision_loan_approval_excluded": "Decision_Loan_Approval" in EXCLUSIONS}

def clean(df: pd.DataFrame) -> tuple[pd.DataFrame, dict]:
    summary = {"raw_row_count": int(len(df)), "raw_column_count": int(df.shape[1])}
    summary["target_distribution_before_cleaning"] = df[TARGET].value_counts(dropna=False).to_dict()
    summary["missing_target_count"] = int(df[TARGET].isna().sum())
    df = df.dropna(subset=[TARGET])                    # never impute target
    summary["rows_removed_missing_target"] = summary["missing_target_count"]
    summary["duplicate_count_before_cleaning"] = int(df.duplicated().sum())
    before = len(df); df = df.drop_duplicates()
    summary["rows_removed_duplicates"] = before - len(df)
    # Clip out-of-scale Likert anomalies (0, 6, 10 observed in raw data) to 1..5
    likert = [c for c in df.select_dtypes("number").columns
              if c not in (TARGET, "Uses_Digital_Finance")]
    df[likert] = df[likert].clip(1, 5)
    summary["final_training_row_count"] = int(len(df))
    summary["target_distribution_after_cleaning"] = df[TARGET].value_counts().to_dict()
    return df, summary

def metrics_for(name, model, Xte, yte):
    proba = model.predict_proba(Xte)
    pos_idx = list(model.classes_).index(1.0)          # never assume [:,1]
    p = proba[:, pos_idx]; pred = (p >= 0.5).astype(int)
    return {
        "model": name,
        "classes_": [float(c) for c in model.classes_],
        "positive_probability_index": pos_idx,
        "accuracy": accuracy_score(yte, pred),
        "roc_auc": roc_auc_score(yte, p),
        "pr_auc": average_precision_score(yte, p),
        "precision": precision_score(yte, pred, zero_division=0),
        "recall": recall_score(yte, pred, zero_division=0),
        "f1": f1_score(yte, pred, zero_division=0),
        "brier": brier_score_loss(yte, p),
        "confusion_matrix": confusion_matrix(yte, pred).tolist(),
    }

def main():
    for d in (ART, EVAL, PROC): d.mkdir(parents=True, exist_ok=True)
    df = pd.read_csv(RAW)
    EVAL.joinpath("leakage_audit.json").write_text(json.dumps(leakage_audit(df), indent=2))
    df, csum = clean(df)
    PROC.joinpath("data_cleaning_summary.json").write_text(json.dumps(csum, indent=2, default=str))

    y = df[TARGET].astype(float)
    X = df.drop(columns=[TARGET, *EXCLUSIONS.keys()])
    num = X.select_dtypes("number").columns.tolist()
    cat = X.select_dtypes("object").columns.tolist()
    Xtr, Xte, ytr, yte = train_test_split(X, y, test_size=0.20,
                                          stratify=y, random_state=RANDOM_STATE)
    # No genuine observation chronology exists -> stratified split (documented).
    pre = ColumnTransformer([
        ("num", Pipeline([("imp", SimpleImputer(strategy="median")),
                          ("sc", StandardScaler())]), num),
        ("cat", Pipeline([("imp", SimpleImputer(strategy="most_frequent")),
                          ("oh", OneHotEncoder(handle_unknown="ignore"))]), cat),
    ])
    spw = (ytr == 0).sum() / max((ytr == 1).sum(), 1)  # training-set only
    candidates = {
        "logistic_regression": LogisticRegression(max_iter=2000, class_weight="balanced"),
        "random_forest": RandomForestClassifier(n_estimators=300, class_weight="balanced",
                                                random_state=RANDOM_STATE, n_jobs=-1),
    }
    try:
        from xgboost import XGBClassifier
        candidates["xgboost"] = XGBClassifier(
            n_estimators=300, max_depth=4, learning_rate=0.08,
            scale_pos_weight=spw, random_state=RANDOM_STATE,
            eval_metric="logloss", n_jobs=-1)
        substitution = None
    except ImportError:
        from sklearn.ensemble import HistGradientBoostingClassifier
        candidates["hist_gradient_boosting"] = HistGradientBoostingClassifier(
            random_state=RANDOM_STATE)
        substitution = "xgboost unavailable -> HistGradientBoostingClassifier substituted"

    results, fitted = [], {}
    for name, clf in candidates.items():
        pipe = Pipeline([("pre", pre), ("clf", clf)]).fit(Xtr, ytr)
        fitted[name] = pipe
        m = metrics_for(name, pipe, Xte, yte)
        m["classes_"] = [float(c) for c in pipe.named_steps["clf"].classes_]
        results.append(m)

    # Selection: PR-AUC > distress recall > ROC-AUC > F1 > (lower) Brier
    best = sorted(results, key=lambda m: (m["pr_auc"], m["recall"], m["roc_auc"],
                                          m["f1"], -m["brier"]), reverse=True)[0]
    for m in results:
        m["selection_status"] = "selected" if m["model"] == best["model"] else "rejected"
    comp = {"results": results, "selection_rationale":
            "Ranked by PR-AUC, then distress recall, ROC-AUC, F1, Brier (minority-class focus).",
            "substitution": substitution,
            "class_balance": {"train_counts": ytr.value_counts().to_dict(),
                              "imbalance_ratio": float(spw)}}
    EVAL.joinpath("model_comparison.json").write_text(json.dumps(comp, indent=2, default=str))

    winner = fitted[best["model"]]
    joblib.dump(winner, ART / "model.joblib")
    ART.joinpath("feature_schema.json").write_text(json.dumps(
        {"numerical": num, "categorical": cat}, indent=2))
    ART.joinpath("model_metrics.json").write_text(json.dumps(best, indent=2, default=str))
    ART.joinpath("model_metadata.json").write_text(json.dumps({
        "model_name": best["model"], "training_date": str(date.today()),
        "dataset_name": RAW.name, "raw_record_count": csum["raw_row_count"],
        "training_record_count": int(len(Xtr)),
        "feature_count_before_encoding": int(X.shape[1]),
        "target_column": TARGET,
        "target_interpretation": "1 = financial distress / higher financial risk",
        "positive_risk_class": 1.0,
        "positive_probability_index": best["positive_probability_index"],
        "validation_method": "stratified train/test split test_size=0.20 random_state=42 "
                             "(no genuine chronology in dataset)",
        "random_state": RANDOM_STATE, "model_status": "trained_model",
        "excluded_leakage_features": list(EXCLUSIONS.keys()),
        "provenance": "public_dataset",
    }, indent=2, default=str))
    print("Selected:", best["model"])

if __name__ == "__main__":
    main()