import pytest
import random
from app.agents.arbiter import validate_proposal
from app.agents.buyer import BuyerAgent
from app.agents.vendor import VendorAgent
from app.schemas.policy import BuyerPolicyEnvelope, VendorPolicyEnvelope
from app.schemas.proposal import ProposalBid, NegotiationState


@pytest.fixture
def buyer_policy():
    return BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)


@pytest.fixture
def vendor_policy():
    return VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)


def test_buyer_always_within_budget(buyer_policy):
    buyer = BuyerAgent(buyer_policy)
    for _ in range(1000):
        state = NegotiationState(session_id="test", current_round=random.randint(1, 10))
        bid = buyer.generate_offer(state)
        assert validate_proposal(bid, buyer_policy, "BUYER") is True


def test_vendor_always_above_floor(vendor_policy):
    vendor = VendorAgent(vendor_policy)
    for _ in range(1000):
        state = NegotiationState(session_id="test", current_round=random.randint(1, 10))
        bid = vendor.generate_offer(state)
        assert validate_proposal(bid, vendor_policy, "VENDOR") is True


def test_buyer_delivery_never_exceeds(buyer_policy):
    buyer = BuyerAgent(buyer_policy)
    for _ in range(1000):
        state = NegotiationState(session_id="test", current_round=random.randint(1, 10))
        bid = buyer.generate_offer(state)
        assert bid.delivery_days <= buyer_policy.max_delivery_days


def test_vendor_delivery_never_below(vendor_policy):
    vendor = VendorAgent(vendor_policy)
    for _ in range(1000):
        state = NegotiationState(session_id="test", current_round=random.randint(1, 10))
        bid = vendor.generate_offer(state)
        assert bid.delivery_days >= vendor_policy.min_delivery_days


def test_buyer_sla_never_below(buyer_policy):
    buyer = BuyerAgent(buyer_policy)
    for _ in range(1000):
        state = NegotiationState(session_id="test", current_round=random.randint(1, 10))
        bid = buyer.generate_offer(state)
        assert bid.sla_percent >= buyer_policy.min_sla_percent


def test_vendor_sla_never_exceeds(vendor_policy):
    vendor = VendorAgent(vendor_policy)
    for _ in range(1000):
        state = NegotiationState(session_id="test", current_round=random.randint(1, 10))
        bid = vendor.generate_offer(state)
        assert bid.sla_percent <= vendor_policy.max_sla_percent


def test_arbiter_blocks_random_violations(buyer_policy, vendor_policy):
    violations_blocked = 0
    for _ in range(1000):
        bid = ProposalBid(
            price=random.uniform(30000, 60000),
            delivery_days=random.randint(10, 60),
            sla_percent=random.uniform(0.5, 7.0),
            agent_type=random.choice(["BUYER", "VENDOR"])
        )
        policy = buyer_policy if bid.agent_type == "BUYER" else vendor_policy
        result = validate_proposal(bid, policy, bid.agent_type)
        if not result:
            violations_blocked += 1

    assert violations_blocked > 0
