from pydantic import BaseModel, Field


class BuyerPolicyEnvelope(BaseModel):
    max_budget: float = Field(..., le=50000, gt=0, description="Maximum budget ceiling")
    max_delivery_days: int = Field(..., le=45, gt=0, description="Latest acceptable delivery")
    min_sla_percent: float = Field(..., ge=2.0, le=100.0, description="Lowest acceptable SLA penalty")


class VendorPolicyEnvelope(BaseModel):
    min_price: float = Field(..., ge=42000, description="Minimum price floor")
    min_delivery_days: int = Field(..., ge=30, description="Fastest possible delivery")
    max_sla_percent: float = Field(..., le=5.0, gt=0, description="Maximum acceptable SLA penalty")


class NegotiationPolicies(BaseModel):
    buyer: BuyerPolicyEnvelope
    vendor: VendorPolicyEnvelope
