"""Turn-based negotiation orchestrator and state machine.

This module is the central coordinator of the negotiation lifecycle.
It creates sessions, initialises buyer and vendor agents (either
deterministic or Lyzr-backed), and drives the alternating offer loop.
Each proposal passes through the Safe AI Arbiter before being persisted.
The orchestrator detects consensus (ACCEPTED) or exhaustion (DEADLOCK)
and triggers contract generation on agreement.
"""

import uuid
from sqlalchemy.orm import Session
from app.models.negotiation import NegotiationSession, NegotiationRound, NegotiationStatus
from app.models.contract import Contract
from app.schemas.policy import BuyerPolicyEnvelope, VendorPolicyEnvelope
from app.schemas.proposal import NegotiationState, ProposalAction, ProposalBid
from app.agents.buyer import BuyerAgent
from app.agents.vendor import VendorAgent
from app.agents.arbiter import validate_with_retry
from app.engine.consensus import generate_contract
from app.config import settings
from app.integrations.lyzr_agent import make_lyzr_buyer, make_lyzr_vendor


def create_session(
    db: Session,
    buyer_policy: BuyerPolicyEnvelope,
    vendor_policy: VendorPolicyEnvelope,
    max_rounds: int = 10
) -> NegotiationSession:
    """Create and persist a new negotiation session.

    Initialises the session with PENDING status and stores the buyer
    and vendor policy envelopes as JSON for later rehydration.

    Args:
        db: Active SQLAlchemy database session.
        buyer_policy: The buyer's hard negotiation limits.
        vendor_policy: The vendor's hard negotiation limits.
        max_rounds: Maximum number of negotiation rounds before deadlock.

    Returns:
        The newly created and committed :class:`NegotiationSession`.
    """
    session = NegotiationSession(
        id=str(uuid.uuid4()),
        status=NegotiationStatus.PENDING,
        buyer_policy=buyer_policy.model_dump(),
        vendor_policy=vendor_policy.model_dump(),
        max_rounds=max_rounds
    )
    db.add(session)
    db.commit()
    db.refresh(session)
    return session


def run_full_negotiation(db: Session, session_id: str) -> NegotiationSession:
    """Execute the complete negotiation loop until consensus or deadlock.

    Instantiates buyer and vendor agents (deterministic or Lyzr-backed),
    then alternates offers until one agent accepts or ``max_rounds`` is
    reached.  Every bid is validated by the Arbiter before persistence.
    On acceptance, a PDF contract is automatically generated.

    Args:
        db: Active SQLAlchemy database session.
        session_id: UUID of the session to negotiate.

    Returns:
        The updated :class:`NegotiationSession` with final status.

    Raises:
        ValueError: If the session ID does not exist.
    """
    session = db.query(NegotiationSession).filter(NegotiationSession.id == session_id).first()
    if not session:
        raise ValueError("Session not found")

    buyer_policy = BuyerPolicyEnvelope(**session.buyer_policy)
    vendor_policy = VendorPolicyEnvelope(**session.vendor_policy)

    if settings.USE_LYZR_AGENTS:
        buyer = make_lyzr_buyer(buyer_policy)
        vendor = make_lyzr_vendor(vendor_policy)
    else:
        buyer = BuyerAgent(buyer_policy)
        vendor = VendorAgent(vendor_policy)

    state = NegotiationState(
        session_id=session.id,
        current_round=1,
        max_rounds=session.max_rounds
    )

    session.status = NegotiationStatus.IN_PROGRESS
    db.commit()

    while state.current_round <= state.max_rounds:
        try:
            buyer_bid = validate_with_retry(buyer, state, buyer_policy)
        except ValueError:
            session.status = NegotiationStatus.DEADLOCK
            session.current_round = state.current_round
            db.commit()
            return session

        _log_round(db, session.id, state.current_round, buyer_bid)
        state.history.append(buyer_bid)

        if buyer_bid.action == ProposalAction.ACCEPT:
            session.status = NegotiationStatus.ACCEPTED
            session.current_round = state.current_round
            db.commit()
            generate_contract(db, session, state)
            return session

        try:
            vendor_bid = validate_with_retry(vendor, state, vendor_policy)
        except ValueError:
            session.status = NegotiationStatus.DEADLOCK
            session.current_round = state.current_round
            db.commit()
            return session

        _log_round(db, session.id, state.current_round, vendor_bid)
        state.history.append(vendor_bid)

        if vendor_bid.action == ProposalAction.ACCEPT:
            session.status = NegotiationStatus.ACCEPTED
            session.current_round = state.current_round
            db.commit()
            generate_contract(db, session, state)
            return session

        state.current_round += 1

    session.status = NegotiationStatus.DEADLOCK
    session.current_round = state.current_round - 1
    db.commit()
    return session


def run_one_step(db: Session, session_id: str) -> NegotiationState:
    """Execute a single buyer-then-vendor round of the negotiation.

    Rehydrates the full history from the database, runs one round
    (buyer offer → arbiter check → vendor counter-offer → arbiter check),
    and persists the results.  Used by the frontend's step-by-step
    Arena mode to give the user real-time visibility into each round.

    Args:
        db: Active SQLAlchemy database session.
        session_id: UUID of the session to advance.

    Returns:
        The updated :class:`NegotiationState` with the new round appended.

    Raises:
        ValueError: If the session ID does not exist.
    """
    session = db.query(NegotiationSession).filter(NegotiationSession.id == session_id).first()
    if not session:
        raise ValueError("Session not found")

    buyer_policy = BuyerPolicyEnvelope(**session.buyer_policy)
    vendor_policy = VendorPolicyEnvelope(**session.vendor_policy)

    if settings.USE_LYZR_AGENTS:
        buyer = make_lyzr_buyer(buyer_policy)
        vendor = make_lyzr_vendor(vendor_policy)
    else:
        buyer = BuyerAgent(buyer_policy)
        vendor = VendorAgent(vendor_policy)

    history_bids = []
    for r in session.rounds:
        history_bids.append(ProposalBid(
            price=r.price,
            delivery_days=r.delivery_days,
            sla_percent=r.sla_percent,
            action=ProposalAction(r.action),
            justification=r.justification,
            round_number=r.round_number,
            agent_type=r.agent_type
        ))

    state = NegotiationState(
        session_id=session.id,
        current_round=session.current_round + 1,
        max_rounds=session.max_rounds,
        history=history_bids,
        is_complete=session.status in [NegotiationStatus.ACCEPTED, NegotiationStatus.DEADLOCK]
    )

    if state.is_complete:
        return state

    try:
        buyer_bid = validate_with_retry(buyer, state, buyer_policy)
    except ValueError:
        session.status = NegotiationStatus.DEADLOCK
        session.current_round = state.current_round
        state.is_complete = True
        db.commit()
        return state

    _log_round(db, session.id, state.current_round, buyer_bid)
    state.history.append(buyer_bid)

    if buyer_bid.action == ProposalAction.ACCEPT:
        session.status = NegotiationStatus.ACCEPTED
        session.current_round = state.current_round
        state.is_complete = True
        state.consensus = buyer_bid
        db.commit()
        generate_contract(db, session, state)
        return state

    try:
        vendor_bid = validate_with_retry(vendor, state, vendor_policy)
    except ValueError:
        session.status = NegotiationStatus.DEADLOCK
        session.current_round = state.current_round
        state.is_complete = True
        db.commit()
        return state

    _log_round(db, session.id, state.current_round, vendor_bid)
    state.history.append(vendor_bid)

    if vendor_bid.action == ProposalAction.ACCEPT:
        session.status = NegotiationStatus.ACCEPTED
        session.current_round = state.current_round
        state.is_complete = True
        state.consensus = vendor_bid
        db.commit()
        generate_contract(db, session, state)
        return state

    if state.current_round >= state.max_rounds:
        session.status = NegotiationStatus.DEADLOCK
        state.is_complete = True
        db.commit()

    session.current_round = state.current_round
    db.commit()
    return state


def _log_round(db: Session, session_id: str, round_number: int, bid: ProposalBid):
    """Persist a single negotiation round to the database.

    Creates a :class:`NegotiationRound` record capturing the agent's
    bid details (price, delivery, SLA, action, justification) for
    audit trail and history dashboard display.
    """
    round_record = NegotiationRound(
        session_id=session_id,
        round_number=round_number,
        agent_type=bid.agent_type,
        price=bid.price,
        delivery_days=bid.delivery_days,
        sla_percent=bid.sla_percent,
        action=bid.action.value,
        justification=bid.justification
    )
    db.add(round_record)
    db.commit()
