"""Exponential-decay concession calculator for game-theoretic negotiation.

Both agents use these functions to determine how much to concede on
price, delivery, and SLA each round.  The concession shrinks
exponentially as rounds increase (controlled by ``discount_factor``),
modelling the economic concept of diminishing marginal concessions.

Formula: ``concession = |gap| × (1 − discount_factor ^ round)``
"""


def calculate_concession(
    base_gap_price: float,
    base_gap_delivery: float,
    base_gap_sla: float,
    round_number: int,
    discount_factor: float = 0.85
) -> dict:
    """Calculate multi-dimensional concession for a given round.

    Args:
        base_gap_price: Absolute gap between the agent's anchor and its limit.
        base_gap_delivery: Absolute gap for delivery days.
        base_gap_sla: Absolute gap for SLA penalty percentage.
        round_number: Current negotiation round (1-indexed).
        discount_factor: Decay rate; lower values yield faster concession.

    Returns:
        Dictionary with ``"price"``, ``"delivery"``, and ``"sla"`` concession amounts.
    """
    factor = 1 - (discount_factor ** round_number)

    return {
        "price": abs(base_gap_price) * factor,
        "delivery": abs(base_gap_delivery) * factor,
        "sla": abs(base_gap_sla) * factor,
    }


def calculate_round_concession(
    initial_value: float,
    target_value: float,
    round_number: int,
    discount_factor: float = 0.85
) -> float:
    """Calculate a single-dimension conceded value for a given round.

    Computes the intermediate value between *initial_value* and
    *target_value* based on the exponential decay factor and the
    current round number.

    Args:
        initial_value: The agent's starting anchor for this dimension.
        target_value: The agent's policy limit for this dimension.
        round_number: Current negotiation round (1-indexed).
        discount_factor: Decay rate; lower values yield faster concession.

    Returns:
        The conceded value for this round.
    """
    base_gap = abs(target_value - initial_value)
    factor = 1 - (discount_factor ** round_number)
    direction = 1 if target_value > initial_value else -1
    return initial_value + (base_gap * factor * direction)
