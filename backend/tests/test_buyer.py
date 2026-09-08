import pytest
from app.agents.buyer import BuyerAgent
from app.schemas.policy import BuyerPolicyEnvelope
from app.schemas.proposal import NegotiationState, ProposalAction


@pytest.fixture
def buyer_policy():
    return BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)


@pytest.fixture
def buyer(buyer_policy):
    return BuyerAgent(buyer_policy)


def test_buyer_initial_offer(buyer):
    state = NegotiationState(session_id="test-123")
    bid = buyer.generate_offer(state)
    assert bid.agent_type == "BUYER"
    assert bid.action == ProposalAction.OFFER
    assert bid.price <= 50000
    assert bid.delivery_days <= 45
    assert bid.sla_percent >= 2.0


def test_buyer_respects_budget(buyer):
    state = NegotiationState(session_id="test-123")
    for _ in range(5):
        bid = buyer.generate_offer(state)
        assert bid.price <= 50000


def test_buyer_respects_delivery(buyer):
    state = NegotiationState(session_id="test-123")
    for _ in range(5):
        bid = buyer.generate_offer(state)
        assert bid.delivery_days <= 45


def test_buyer_respects_sla(buyer):
    state = NegotiationState(session_id="test-123")
    for _ in range(5):
        bid = buyer.generate_offer(state)
        assert bid.sla_percent >= 2.0


def test_buyer_accepts_valid_vendor_offer(buyer, buyer_policy):
    from app.schemas.proposal import ProposalBid

    state = NegotiationState(session_id="test-123")
    vendor_bid = ProposalBid(
        price=45000,
        delivery_days=35,
        sla_percent=3.0,
        agent_type="VENDOR"
    )
    state.history.append(vendor_bid)
    bid = buyer.generate_offer(state)
    assert bid.action == ProposalAction.ACCEPT


def test_buyer_counters_out_of_bounds(buyer, buyer_policy):
    from app.schemas.proposal import ProposalBid

    state = NegotiationState(session_id="test-123")
    vendor_bid = ProposalBid(
        price=60000,
        delivery_days=50,
        sla_percent=1.0,
        agent_type="VENDOR"
    )
    state.history.append(vendor_bid)
    bid = buyer.generate_offer(state)
    assert bid.action == ProposalAction.OFFER
    assert bid.price <= 50000
