"""Forensic inspection of the raw public SME CSV. Source of truth for schema."""
import json, pathlib
import pandas as pd

RAW = pathlib.Path(__file__).resolve().parents[1] / "data/raw/Finanical_data_sme.csv"
OUT = pathlib.Path(__file__).resolve().parents[1] / "data/processed/dataset_schema.json"

def inspect():
    df = pd.read_csv(RAW)
    low_card = {c: sorted(df[c].dropna().unique().tolist())
                for c in df.columns if df[c].nunique(dropna=True) <= 12}
    schema = {
        "filename": RAW.name,
        "rows": int(len(df)),
        "columns": int(df.shape[1]),
        "column_names": list(df.columns),
        "dtypes": {c: str(t) for c, t in df.dtypes.items()},
        "missing_per_column": {c: int(df[c].isna().sum()) for c in df.columns},
        "duplicate_rows": int(df.duplicated().sum()),
        "low_cardinality_uniques": low_card,
        "numerical_columns": df.select_dtypes("number").columns.tolist(),
        "categorical_columns": df.select_dtypes("object").columns.tolist(),
        "candidate_targets": [c for c in df.columns if "distress" in c.lower()],
        "target_distribution": df["Financial_Distress"].value_counts(dropna=False).to_dict()
            if "Financial_Distress" in df else None,
        "out_of_scale_flags": {
            c: int(((df[c] < 0) | (df[c] > 5)).sum())
            for c in df.select_dtypes("number").columns
            if c not in ("Uses_Digital_Finance", "Financial_Distress")
        },
        "provenance": "public_dataset",
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(json.dumps(schema, indent=2, default=str))
    print(json.dumps(schema, indent=2, default=str))

if __name__ == "__main__":
    inspect()