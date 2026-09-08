import pytest
from app.engine.concession import calculate_concession, calculate_round_concession


def test_concession_round_1():
    result = calculate_concession(
        base_gap_price=10000,
        base_gap_delivery=25,
        base_gap_sla=3.0,
        round_number=1,
        discount_factor=0.85
    )
    assert result["price"] > 0
    assert result["delivery"] > 0
    assert result["sla"] > 0


def test_concession_increases_over_rounds():
    r1 = calculate_concession(10000, 25, 3.0, 1)
    r5 = calculate_concession(10000, 25, 3.0, 5)
    r10 = calculate_concession(10000, 25, 3.0, 10)

    assert r1["price"] < r5["price"] < r10["price"]


def test_concession_approaches_gap():
    gap = 10000
    r1 = calculate_concession(gap, 25, 3.0, 1)
    r100 = calculate_concession(gap, 25, 3.0, 100)
    assert r100["price"] > r1["price"]


def test_concession_with_zero_gap():
    result = calculate_concession(0, 0, 0, 1)
    assert result["price"] == 0
    assert result["delivery"] == 0
    assert result["sla"] == 0


def test_concession_custom_discount():
    r1 = calculate_concession(10000, 25, 3.0, 1, discount_factor=0.5)
    r2 = calculate_concession(10000, 25, 3.0, 1, discount_factor=0.9)
    assert r1["price"] > r2["price"]


def test_round_concession():
    result = calculate_round_concession(
        initial_value=40000,
        target_value=50000,
        round_number=1
    )
    assert 40000 < result < 50000


def test_round_convergence():
    r1 = calculate_round_concession(40000, 50000, 1)
    r5 = calculate_round_concession(40000, 50000, 5)
    r10 = calculate_round_concession(40000, 50000, 10)
    assert r1 < r5 < r10
