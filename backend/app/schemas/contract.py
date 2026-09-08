from pydantic import BaseModel, Field
from datetime import datetime, UTC


class ContractPayload(BaseModel):
    session_id: str
    final_price: float = Field(..., gt=0)
    final_delivery_days: int = Field(..., gt=0)
    final_sla_percent: float = Field(..., gt=0, le=100)
    buyer_justification: str = ""
    vendor_justification: str = ""
    total_rounds: int = Field(..., ge=1)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    pdf_file_path: str = ""
