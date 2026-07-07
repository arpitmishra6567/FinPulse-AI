"""Request/response schemas for the Phase 2 REST layer."""
from typing import Optional
from pydantic import BaseModel, model_validator


class SimulationRequest(BaseModel):
    receivable_days: Optional[float] = None
    cash_reserve: Optional[float] = None
    customer_concentration: Optional[float] = None
    debt_service_ratio: Optional[float] = None

    @model_validator(mode="after")
    def at_least_one(self):
        if not self.changes():
            raise ValueError("Provide at least one simulatable field: receivable_days, "
                             "cash_reserve, customer_concentration, debt_service_ratio.")
        return self

    def changes(self) -> dict:
        return {k: v for k, v in self.model_dump().items() if v is not None}