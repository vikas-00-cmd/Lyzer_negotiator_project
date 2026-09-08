from fastapi import APIRouter, Request, Depends, HTTPException
from sqlalchemy.orm import Session
from pydantic import BaseModel, ValidationError
from app.database import get_db
from app.limits import limiter
from app.schemas.policy import NegotiationPolicies
from app.schemas.proposal import NegotiationState, ProposalBid, ProposalAction
from app.models.negotiation import NegotiationSession, NegotiationRound, NegotiationStatus
from app.engine.orchestrator import create_session, run_full_negotiation, run_one_step
import json

router = APIRouter(prefix="/negotiation", tags=["negotiation"])

class StartRequest(BaseModel):
    buyer_max_budget: float
    buyer_max_delivery_days: int
    buyer_min_sla_percent: float
    vendor_min_price: float
    vendor_min_delivery_days: int
    vendor_max_sla_percent: float
    max_rounds: int = 10
class SessionResponse(BaseModel):
    id: str
    status: str
    current_round: int
    max_rounds: int
    buyer_policy: dict
    vendor_policy: dict

class SessionListResponse(SessionResponse):
    created_at: str

class RoundResponse(BaseModel):
    round_number: int
    agent_type: str
    price: float
    delivery_days: int
    sla_percent: float
    action: str
    justification: str

@router.get("/sessions", response_model=list[SessionListResponse])
def list_sessions(db: Session = Depends(get_db)):
    sessions = db.query(NegotiationSession).order_by(NegotiationSession.created_at.desc()).limit(20).all()
    return [
        SessionListResponse(
            id=s.id,
            status=s.status.value,
            current_round=s.current_round,
            max_rounds=s.max_rounds,
            buyer_policy=s.buyer_policy,
            vendor_policy=s.vendor_policy,
            created_at=s.created_at.isoformat()
        )
        for s in sessions
    ]


@router.post("/start", response_model=SessionResponse)
@limiter.limit("5/minute")
async def start_negotiation(request: Request, req: StartRequest, db: Session = Depends(get_db)):
    from app.schemas.policy import BuyerPolicyEnvelope, VendorPolicyEnvelope

    try:
        buyer_policy = BuyerPolicyEnvelope(
            max_budget=req.buyer_max_budget,
            max_delivery_days=req.buyer_max_delivery_days,
            min_sla_percent=req.buyer_min_sla_percent
        )
        vendor_policy = VendorPolicyEnvelope(
            min_price=req.vendor_min_price,
            min_delivery_days=req.vendor_min_delivery_days,
            max_sla_percent=req.vendor_max_sla_percent
        )
    except ValidationError as e:
        raise HTTPException(status_code=422, detail=e.errors())

    session = create_session(db, buyer_policy, vendor_policy, req.max_rounds)
    return SessionResponse(
        id=session.id,
        status=session.status.value,
        current_round=session.current_round,
        max_rounds=session.max_rounds,
        buyer_policy=session.buyer_policy,
        vendor_policy=session.vendor_policy
    )


@router.post("/{session_id}/auto", response_model=SessionResponse)
@limiter.limit("5/minute")
async def auto_negotiate(request: Request, session_id: str, db: Session = Depends(get_db)):
    try:
        session = run_full_negotiation(db, session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return SessionResponse(
        id=session.id,
        status=session.status.value,
        current_round=session.current_round,
        max_rounds=session.max_rounds,
        buyer_policy=session.buyer_policy,
        vendor_policy=session.vendor_policy
    )


@router.get("/{session_id}/status", response_model=SessionResponse)
def get_status(session_id: str, db: Session = Depends(get_db)):
    session = db.query(NegotiationSession).filter(NegotiationSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    return SessionResponse(
        id=session.id,
        status=session.status.value,
        current_round=session.current_round,
        max_rounds=session.max_rounds,
        buyer_policy=session.buyer_policy,
        vendor_policy=session.vendor_policy
    )


@router.post("/{session_id}/step")
@limiter.limit("20/minute")
async def step_negotiation(request: Request, session_id: str, db: Session = Depends(get_db)):
    session = db.query(NegotiationSession).filter(NegotiationSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    TERMINAL = {NegotiationStatus.ACCEPTED, NegotiationStatus.DEADLOCK, NegotiationStatus.ENDED}
    if session.status in TERMINAL:
        raise HTTPException(
            status_code=400,
            detail=f"Negotiation already concluded. Final status: {session.status.value}"
        )

    try:
        state = run_one_step(db, session_id)
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))

    return {
        "session_id": state.session_id,
        "current_round": state.current_round,
        "is_complete": state.is_complete,
        "history": [bid.model_dump() for bid in state.history],
        "consensus": state.consensus.model_dump() if state.consensus else None
    }


@router.get("/{session_id}/rounds", response_model=list[RoundResponse])
def get_rounds(session_id: str, db: Session = Depends(get_db)):
    session = db.query(NegotiationSession).filter(NegotiationSession.id == session_id).first()
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")

    rounds = db.query(NegotiationRound).filter(
        NegotiationRound.session_id == session_id
    ).order_by(NegotiationRound.round_number).all()

    return [
        RoundResponse(
            round_number=r.round_number,
            agent_type=r.agent_type,
            price=r.price,
            delivery_days=r.delivery_days,
            sla_percent=r.sla_percent,
            action=r.action,
            justification=r.justification
        )
        for r in rounds
    ]
