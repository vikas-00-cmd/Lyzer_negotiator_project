import pytest
from pydantic import ValidationError
from app.schemas.policy import BuyerPolicyEnvelope, VendorPolicyEnvelope, NegotiationPolicies


def test_buyer_policy_valid():
    policy = BuyerPolicyEnvelope(max_budget=48000, max_delivery_days=40, min_sla_percent=3.0)
    assert policy.max_budget == 48000
    assert policy.max_delivery_days == 40
    assert policy.min_sla_percent == 3.0


def test_buyer_policy_max_budget_boundary():
    policy = BuyerPolicyEnvelope(max_budget=50000, max_delivery_days=45, min_sla_percent=2.0)
    assert policy.max_budget == 50000


def test_buyer_policy_exceeds_budget():
    with pytest.raises(ValidationError):
        BuyerPolicyEnvelope(max_budget=55000, max_delivery_days=40, min_sla_percent=3.0)


def test_buyer_policy_exceeds_delivery():
    with pytest.raises(ValidationError):
        BuyerPolicyEnvelope(max_budget=48000, max_delivery_days=50, min_sla_percent=3.0)


def test_buyer_policy_below_sla():
    with pytest.raises(ValidationError):
        BuyerPolicyEnvelope(max_budget=48000, max_delivery_days=40, min_sla_percent=1.0)


def test_vendor_policy_valid():
    policy = VendorPolicyEnvelope(min_price=43000, min_delivery_days=32, max_sla_percent=4.5)
    assert policy.min_price == 43000
    assert policy.min_delivery_days == 32
    assert policy.max_sla_percent == 4.5


def test_vendor_policy_min_price_boundary():
    policy = VendorPolicyEnvelope(min_price=42000, min_delivery_days=30, max_sla_percent=5.0)
    assert policy.min_price == 42000


def test_vendor_policy_below_min_price():
    with pytest.raises(ValidationError):
        VendorPolicyEnvelope(min_price=40000, min_delivery_days=32, max_sla_percent=4.5)


def test_vendor_policy_below_delivery():
    with pytest.raises(ValidationError):
        VendorPolicyEnvelope(min_price=43000, min_delivery_days=25, max_sla_percent=4.5)


def test_vendor_policy_exceeds_sla():
    with pytest.raises(ValidationError):
        VendorPolicyEnvelope(min_price=43000, min_delivery_days=32, max_sla_percent=6.0)


def test_negotiation_policies_combined():
    policies = NegotiationPolicies(
        buyer=BuyerPolicyEnvelope(max_budget=48000, max_delivery_days=40, min_sla_percent=3.0),
        vendor=VendorPolicyEnvelope(min_price=43000, min_delivery_days=32, max_sla_percent=4.5)
    )
    assert policies.buyer.max_budget == 48000
    assert policies.vendor.min_price == 43000
