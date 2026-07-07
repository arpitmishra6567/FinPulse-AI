# Responsible AI

Allowed vocabulary: Financial Health, Financial Distress Probability, Risk Signal,
Unusual Financial Pattern, Credit Readiness, Indicative Assessment, Human Review
Recommended, Decision Support.

Never claimed: Loan Approved · RBI Approved · IDBI Endorsed · Fraud Detected ·
Guaranteed Credit · Production Ready for IDBI. No protected demographics are used
for scoring. Missing data lowers **confidence**, never auto-assigns critical risk.
Neutral 0.5 fallback is never presented as a trained prediction. SHAP is shown only
when genuinely computed. Enforced by tests (`test_responsible_terminology`).