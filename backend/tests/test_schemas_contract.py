import pytest
from pydantic import ValidationError
from app.schemas.contract import ContractPayload


def test_contract_payload_valid():
    payload = ContractPayload(
        session_id="test-123",
        final_price=45500,
        final_delivery_days=35,
        final_sla_percent=3.5,
        total_rounds=3
    )
    assert payload.session_id == "test-123"
    assert payload.final_price == 45500


def test_contract_payload_negative_price():
    with pytest.raises(ValidationError):
        ContractPayload(
            session_id="test-123",
            final_price=-100,
            final_delivery_days=35,
            final_sla_percent=3.5,
            total_rounds=3
        )


def test_contract_payload_zero_delivery():
    with pytest.raises(ValidationError):
        ContractPayload(
            session_id="test-123",
            final_price=45500,
            final_delivery_days=0,
            final_sla_percent=3.5,
            total_rounds=3
        )


def test_contract_payload_zero_rounds():
    with pytest.raises(ValidationError):
        ContractPayload(
            session_id="test-123",
            final_price=45500,
            final_delivery_days=35,
            final_sla_percent=3.5,
            total_rounds=0
        )


def test_contract_payload_with_justifications():
    payload = ContractPayload(
        session_id="test-123",
        final_price=45500,
        final_delivery_days=35,
        final_sla_percent=3.5,
        buyer_justification="Buyer accepted",
        vendor_justification="Vendor agreed",
        total_rounds=3
    )
    assert payload.buyer_justification == "Buyer accepted"
    assert payload.vendor_justification == "Vendor agreed"
