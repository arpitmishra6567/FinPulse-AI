"""Adapter layer: 'Swap the connector, not the intelligence engine.'"""
import json, pathlib
import pandas as pd
from backend.app.schemas.finpulse import FinPulseFinancials

class BaseFinancialDataAdapter:
    provenance = "public_dataset"
    def load(self) -> list[FinPulseFinancials]: raise NotImplementedError

class PublicSMEDataAdapter(BaseFinancialDataAdapter):
    """Maps ONLY semantically valid fields from the survey CSV.
    GST/UPI/EPFO/AA fields DO NOT exist in the public CSV -> left unavailable."""
    MAPPING = [
        {"raw_column": "Industry_Sector", "finpulse_feature": "sector",
         "transformation": "code passthrough", "source_type": "public_dataset"},
        {"raw_column": "SME_Age", "finpulse_feature": "business_age_years",
         "transformation": "ordinal band midpoint {1:1.5,2:5,3:10}", "source_type": "public_dataset"},
        {"raw_column": "Liquidity_Stability", "finpulse_feature": "liquidity_ratio",
         "transformation": "Likert 1-5 -> proxy ratio 0.5+0.4*(v-1)", "source_type": "public_dataset"},
        {"raw_column": "Annual_Revenue_Category", "finpulse_feature": "monthly_revenue",
         "transformation": "band proxy Low=1.5L, Medium=6L, High=20L (INR)", "source_type": "public_dataset"},
        {"raw_column": "Literacy_Credit_Knowledge", "finpulse_feature": "repayment_consistency",
         "transformation": "Likert/5 -> 0..1 weak proxy (flagged low-confidence)",
         "source_type": "public_dataset"},
    ]
    def __init__(self, csv_path):
        self.csv_path = pathlib.Path(csv_path)
    def write_mapping(self, out_path):
        pathlib.Path(out_path).write_text(json.dumps(self.MAPPING, indent=2))
    def load(self):
        df = pd.read_csv(self.csv_path)
        rev = {"Low": 150_000, "Medium": 600_000, "High": 2_000_000}
        age = {1: 1.5, 2: 5, 3: 10}
        out = []
        for i, r in df.iterrows():
            out.append(FinPulseFinancials(
                msme_id=f"PUB-{i:05d}", sector=str(r.get("Industry_Sector")),
                business_age_years=age.get(r.get("SME_Age")),
                liquidity_ratio=None if pd.isna(r.get("Liquidity_Stability"))
                    else 0.5 + 0.4 * (float(r["Liquidity_Stability"]) - 1),
                monthly_revenue=rev.get(r.get("Annual_Revenue_Category")),
                repayment_consistency=None if pd.isna(r.get("Literacy_Credit_Knowledge"))
                    else min(float(r["Literacy_Credit_Knowledge"]), 5) / 5,
                provenance="public_dataset"))
        return out

class DemoMSMEDataAdapter(BaseFinancialDataAdapter):
    provenance = "synthetic_demo"
    def __init__(self, demo_dir): self.demo_dir = pathlib.Path(demo_dir)
    def load(self):
        recs = json.loads((self.demo_dir / "demo_msmes.json").read_text())
        return [FinPulseFinancials(**r["latest"]) for r in recs]
    def load_history(self):
        return json.loads((self.demo_dir / "demo_msmes.json").read_text())

class FutureIDBISandboxAdapter(BaseFinancialDataAdapter):
    """Interface stub only. No real IDBI endpoints are invented."""
    provenance = "future_sandbox"
    def load(self):
        raise NotImplementedError("future_sandbox: pending sandbox access if shortlisted")