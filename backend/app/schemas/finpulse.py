from typing import Optional, Literal
from pydantic import BaseModel

Provenance = Literal["public_dataset", "synthetic_demo", "future_sandbox"]

class FinPulseFinancials(BaseModel):
    msme_id: str
    business_name: Optional[str] = None
    sector: Optional[str] = None
    business_age_years: Optional[float] = None
    monthly_revenue: Optional[float] = None
    revenue_growth_rate: Optional[float] = None
    revenue_volatility: Optional[float] = None
    cash_inflows: Optional[float] = None
    cash_outflows: Optional[float] = None
    operating_expenses: Optional[float] = None
    cash_reserve: Optional[float] = None
    current_assets: Optional[float] = None
    current_liabilities: Optional[float] = None
    liquidity_ratio: Optional[float] = None
    total_debt: Optional[float] = None
    monthly_debt_service: Optional[float] = None
    debt_service_ratio: Optional[float] = None
    existing_credit_exposure: Optional[float] = None
    receivable_days: Optional[float] = None
    payable_days: Optional[float] = None
    customer_concentration: Optional[float] = None
    gst_turnover_growth: Optional[float] = None       # synthetic_demo only
    gst_filing_consistency: Optional[float] = None    # synthetic_demo only
    upi_inflow_stability: Optional[float] = None      # synthetic_demo only
    upi_transaction_growth: Optional[float] = None    # synthetic_demo only
    employee_count: Optional[int] = None
    employee_growth_rate: Optional[float] = None
    epfo_contribution_consistency: Optional[float] = None  # synthetic_demo only
    repayment_consistency: Optional[float] = None
    provenance: Provenance = "public_dataset"