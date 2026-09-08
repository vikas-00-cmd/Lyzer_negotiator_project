import uuid
from datetime import datetime, UTC
from sqlalchemy import Column, String, Integer, Float, DateTime, ForeignKey, JSON, Enum as SAEnum
from sqlalchemy.orm import relationship
from app.database import Base
import enum


class NegotiationStatus(str, enum.Enum):
    PENDING = "PENDING"
    IN_PROGRESS = "IN_PROGRESS"
    ACCEPTED = "ACCEPTED"
    DEADLOCK = "DEADLOCK"
    ENDED = "ENDED"


class NegotiationSession(Base):
    __tablename__ = "negotiation_sessions"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    status = Column(SAEnum(NegotiationStatus), default=NegotiationStatus.PENDING)
    buyer_policy = Column(JSON, nullable=False)
    vendor_policy = Column(JSON, nullable=False)
    max_rounds = Column(Integer, default=10)
    current_round = Column(Integer, default=0)
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))
    updated_at = Column(DateTime, default=lambda: datetime.now(UTC), onupdate=lambda: datetime.now(UTC))

    rounds = relationship("NegotiationRound", back_populates="session", cascade="all, delete-orphan")
    contract = relationship("Contract", back_populates="session", uselist=False)


class NegotiationRound(Base):
    __tablename__ = "negotiation_rounds"

    id = Column(String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    session_id = Column(String(36), ForeignKey("negotiation_sessions.id"), nullable=False)
    round_number = Column(Integer, nullable=False)
    agent_type = Column(String(10), nullable=False)
    price = Column(Float, nullable=False)
    delivery_days = Column(Integer, nullable=False)
    sla_percent = Column(Float, nullable=False)
    action = Column(String(20), nullable=False)
    justification = Column(String(500), default="")
    created_at = Column(DateTime, default=lambda: datetime.now(UTC))

    session = relationship("NegotiationSession", back_populates="rounds")
