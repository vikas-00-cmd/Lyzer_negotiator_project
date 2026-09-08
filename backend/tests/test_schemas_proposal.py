import pytest
from pydantic import ValidationError
from app.schemas.proposal import ProposalAction, ProposalBid, NegotiationState


def test_proposal_action_enum():
    assert ProposalAction.OFFER.value == "OFFER"
    assert ProposalAction.ACCEPT.value == "ACCEPT"
    assert ProposalAction.END_NEGOTIATION.value == "END_NEGOTIATION"


def test_proposal_bid_valid():
    bid = ProposalBid(
        price=45000,
        delivery_days=30,
        sla_percent=3.5,
        action=ProposalAction.OFFER,
        justification="Test offer",
        round_number=1,
        agent_type="BUYER"
    )
    assert bid.price == 45000
    assert bid.agent_type == "BUYER"


def test_proposal_bid_default_action():
    bid = ProposalBid(
        price=45000,
        delivery_days=30,
        sla_percent=3.5,
        agent_type="BUYER"
    )
    assert bid.action == ProposalAction.OFFER


def test_proposal_bid_negative_price():
    with pytest.raises(ValidationError):
        ProposalBid(price=-100, delivery_days=30, sla_percent=3.5, agent_type="BUYER")


def test_proposal_bid_zero_delivery():
    with pytest.raises(ValidationError):
        ProposalBid(price=45000, delivery_days=0, sla_percent=3.5, agent_type="BUYER")


def test_proposal_bid_negative_sla():
    with pytest.raises(ValidationError):
        ProposalBid(price=45000, delivery_days=30, sla_percent=-1.0, agent_type="BUYER")


def test_proposal_bid_sla_exceeds_100():
    with pytest.raises(ValidationError):
        ProposalBid(price=45000, delivery_days=30, sla_percent=150.0, agent_type="BUYER")


def test_proposal_bid_zero_round():
    with pytest.raises(ValidationError):
        ProposalBid(price=45000, delivery_days=30, sla_percent=3.5, agent_type="BUYER", round_number=0)


def test_negotiation_state_valid():
    state = NegotiationState(session_id="test-123")
    assert state.session_id == "test-123"
    assert state.current_round == 1
    assert state.is_complete is False
    assert state.history == []


def test_negotiation_state_with_history():
    bid = ProposalBid(price=45000, delivery_days=30, sla_percent=3.5, agent_type="BUYER")
    state = NegotiationState(session_id="test-123", history=[bid])
    assert len(state.history) == 1
