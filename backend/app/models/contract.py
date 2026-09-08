import uuid
from datetime import datetime, UTC
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey
from sqlalchemy.orm import relationship
from app.database import Base


class Contract(Base):
    __tablename__ = "contracts"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("negotiation_sessions.id"), nullable=False, unique=True)
    final_price = Column(Float, nullable=False)
    final_delivery_days = Column(Integer, nullable=False)
    final_sla_percent = Column(Float, nullable=False)
    pdf_file_path = Column(String(500), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    session = relationship("NegotiationSession", back_populates="contract")
