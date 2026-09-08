import pytest
from app.agents.arbiter import validate_proposal
from app.schemas.proposal import ProposalBid, ProposalAction
from app.schemas.policy import BuyerPolicyEnvelope, VendorPolicyEnvelope


@pytest.fixture
def buyer_policy():
    return BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)


@pytest.fixture
def vendor_policy():
    return VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)


def test_buyer_valid_offer(buyer_policy):
    bid = ProposalBid(price=45000, delivery_days=30, sla_percent=3.5, agent_type="BUYER")
    assert validate_proposal(bid, buyer_policy, "BUYER") is True


def test_buyer_exceeds_budget(buyer_policy):
    bid = ProposalBid(price=55000, delivery_days=30, sla_percent=3.5, agent_type="BUYER")
    assert validate_proposal(bid, buyer_policy, "BUYER") is False


def test_buyer_exceeds_delivery(buyer_policy):
    bid = ProposalBid(price=45000, delivery_days=50, sla_percent=3.5, agent_type="BUYER")
    assert validate_proposal(bid, buyer_policy, "BUYER") is False


def test_buyer_below_sla(buyer_policy):
    bid = ProposalBid(price=45000, delivery_days=30, sla_percent=1.0, agent_type="BUYER")
    assert validate_proposal(bid, buyer_policy, "BUYER") is False


def test_buyer_at_exact_boundary(buyer_policy):
    bid = ProposalBid(price=50000, delivery_days=45, sla_percent=2.0, agent_type="BUYER")
    assert validate_proposal(bid, buyer_policy, "BUYER") is True


def test_vendor_valid_offer(vendor_policy):
    bid = ProposalBid(price=45000, delivery_days=35, sla_percent=3.5, agent_type="VENDOR")
    assert validate_proposal(bid, vendor_policy, "VENDOR") is True


def test_vendor_below_min_price(vendor_policy):
    bid = ProposalBid(price=40000, delivery_days=35, sla_percent=3.5, agent_type="VENDOR")
    assert validate_proposal(bid, vendor_policy, "VENDOR") is False


def test_vendor_below_delivery(vendor_policy):
    bid = ProposalBid(price=45000, delivery_days=25, sla_percent=3.5, agent_type="VENDOR")
    assert validate_proposal(bid, vendor_policy, "VENDOR") is False


def test_vendor_exceeds_sla(vendor_policy):
    bid = ProposalBid(price=45000, delivery_days=35, sla_percent=6.0, agent_type="VENDOR")
    assert validate_proposal(bid, vendor_policy, "VENDOR") is False


def test_vendor_at_exact_boundary(vendor_policy):
    bid = ProposalBid(price=42000, delivery_days=30, sla_percent=5.0, agent_type="VENDOR")
    assert validate_proposal(bid, vendor_policy, "VENDOR") is True


def test_accept_action_always_valid(buyer_policy):
    bid = ProposalBid(price=999999, delivery_days=999, sla_percent=100, action=ProposalAction.ACCEPT, agent_type="BUYER")
    assert validate_proposal(bid, buyer_policy, "BUYER") is True


def test_end_negotiation_always_valid(vendor_policy):
    bid = ProposalBid(price=1, delivery_days=1, sla_percent=1, action=ProposalAction.END_NEGOTIATION, agent_type="VENDOR")
    assert validate_proposal(bid, vendor_policy, "VENDOR") is True
