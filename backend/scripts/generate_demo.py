"""Deterministic synthetic_demo MSMEs: ~100 firms x 12 months, logical financial dynamics."""
import json, pathlib, random
import numpy as np

BASE = pathlib.Path(__file__).resolve().parents[1] / "data/demo"
SECTORS = ["Textiles","Manufacturing","Food Processing","Automotive Components","Retail",
           "Logistics","IT Services","Packaging","Agriculture Processing","Engineering"]
ARCHETYPES = (["improving"]*14 + ["deteriorating"]*14 + ["sudden_deterioration"]*6 +
              ["recovery"]*6 + ["low_confidence"]*6 + ["stable_good"]*24 +
              ["stable_watch"]*18 + ["stable_weak"]*12)  # 100

def month(prev, arch, t, rng):
    drift = {"improving": .02, "deteriorating": -.03, "recovery": (-.04 if t < 5 else .05),
             "sudden_deterioration": (0 if t < 8 else -.12), "stable_good": .003,
             "stable_watch": 0.0, "stable_weak": -.005, "low_confidence": 0.0}[arch]
    rev = max(prev["monthly_revenue"] * (1 + drift + rng.normal(0, .03)), 20_000)
    opex = rev * rng.uniform(.55, .8)
    debt = max(prev["total_debt"] * (1 + (-.01 if drift > 0 else .02)), 0)
    dsr = min((debt * .025) / max(rev, 1), 1.5)
    reserve = max(prev["cash_reserve"] + (rev - opex - debt * .025) * .4, 0)
    liq = max(.3, min(reserve / max(opex, 1) + rng.uniform(.2, .5), 3.5))
    m = {**prev, "monthly_revenue": round(rev), "operating_expenses": round(opex),
         "cash_inflows": round(rev * rng.uniform(.9, 1.05)),
         "cash_outflows": round(opex * rng.uniform(.95, 1.1)),
         "cash_reserve": round(reserve), "liquidity_ratio": round(liq, 2),
         "total_debt": round(debt), "monthly_debt_service": round(debt * .025),
         "debt_service_ratio": round(dsr, 3),
         "receivable_days": round(max(15, prev["receivable_days"] - drift * 100 + rng.normal(0, 3))),
         "customer_concentration": round(min(.95, max(.05,
             prev["customer_concentration"] - drift * .5 + rng.normal(0, .02))), 2),
         "gst_filing_consistency": round(min(1, max(0, .95 + drift * 2 + rng.normal(0, .03))), 2),
         "upi_inflow_stability": round(min(1, max(0, .8 + drift * 3 + rng.normal(0, .05))), 2),
         "epfo_contribution_consistency": round(min(1, max(0, .9 + drift + rng.normal(0, .04))), 2),
         "repayment_consistency": round(min(1, max(0, .9 + drift * 2)), 2),
         "employee_growth_rate": round(drift * (1 if drift > 0 else 1.5), 3),
         "revenue_growth_rate": round(drift, 3)}
    # Carry real numeric state forward in `m`; expose a redacted snapshot for output.
    m["_low_conf"] = bool(prev.get("_low_conf"))
    return m

def main():
    rng = np.random.default_rng(42); random.seed(42)
    firms = []
    for i, arch in enumerate(ARCHETYPES):
        base = {"msme_id": f"DEMO-{i:03d}", "business_name": f"{random.choice(SECTORS)} Ventures {i}",
                "sector": SECTORS[i % 10], "business_age_years": int(rng.integers(2, 20)),
                "monthly_revenue": float(rng.integers(200_000, 3_000_000)),
                "operating_expenses": 0, "cash_reserve": float(rng.integers(50_000, 800_000)),
                "total_debt": float(rng.integers(0, 4_000_000)), "receivable_days": 45.0,
                "customer_concentration": float(rng.uniform(.1, .7)),
                "employee_count": int(rng.integers(4, 120)),
                "revenue_volatility": round(float(rng.uniform(.02, .15)), 3),
                "provenance": "synthetic_demo", "_low_conf": arch == "low_confidence"}
        hist, cur = [], base
        REDACT = ("gst_filing_consistency", "upi_inflow_stability",
                  "epfo_contribution_consistency", "receivable_days", "cash_reserve")
        for t in range(12):
            cur = month(cur, arch, t, rng)
            snap = {k: v for k, v in cur.items() if k != "_low_conf"}
            if cur.get("_low_conf"):
                for k in REDACT:
                    snap[k] = None
            hist.append(snap)
        firms.append({"msme_id": base["msme_id"], "archetype": arch,
                      "history": hist, "latest": hist[-1]})
    BASE.mkdir(parents=True, exist_ok=True)
    (BASE / "demo_msmes.json").write_text(json.dumps(firms, indent=1))
    print(f"Generated {len(firms)} demo MSMEs (synthetic_demo)")

if __name__ == "__main__":
    main()