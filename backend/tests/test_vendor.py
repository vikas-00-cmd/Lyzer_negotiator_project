import pytest
from app.agents.vendor import VendorAgent
from app.schemas.policy import VendorPolicyEnvelope
from app.schemas.proposal import NegotiationState, ProposalAction


@pytest.fixture
def vendor_policy():
    return VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)


@pytest.fixture
def vendor(vendor_policy):
    return VendorAgent(vendor_policy)


def test_vendor_initial_offer(vendor):
    state = NegotiationState(session_id="test-123")
    bid = vendor.generate_offer(state)
    assert bid.agent_type == "VENDOR"
    assert bid.action == ProposalAction.OFFER
    assert bid.price >= 42000
    assert bid.delivery_days >= 30
    assert bid.sla_percent <= 5.0


def test_vendor_respects_min_price(vendor):
    state = NegotiationState(session_id="test-123")
    for _ in range(5):
        bid = vendor.generate_offer(state)
        assert bid.price >= 42000


def test_vendor_respects_delivery(vendor):
    state = NegotiationState(session_id="test-123")
    for _ in range(5):
        bid = vendor.generate_offer(state)
        assert bid.delivery_days >= 30


def test_vendor_respects_sla(vendor):
    state = NegotiationState(session_id="test-123")
    for _ in range(5):
        bid = vendor.generate_offer(state)
        assert bid.sla_percent <= 5.0


def test_vendor_accepts_valid_buyer_offer(vendor, vendor_policy):
    from app.schemas.proposal import ProposalBid

    state = NegotiationState(session_id="test-123")
    buyer_bid = ProposalBid(
        price=45000,
        delivery_days=35,
        sla_percent=3.0,
        agent_type="BUYER"
    )
    state.history.append(buyer_bid)
    bid = vendor.generate_offer(state)
    assert bid.action == ProposalAction.ACCEPT


def test_vendor_counters_out_of_bounds(vendor, vendor_policy):
    from app.schemas.proposal import ProposalBid

    state = NegotiationState(session_id="test-123")
    buyer_bid = ProposalBid(
        price=40000,
        delivery_days=20,
        sla_percent=6.0,
        agent_type="BUYER"
    )
    state.history.append(buyer_bid)
    bid = vendor.generate_offer(state)
    assert bid.action == ProposalAction.OFFER
    assert bid.price >= 42000
