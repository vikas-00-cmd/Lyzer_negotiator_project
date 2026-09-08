def calculate_concession(
    base_gap_price: float,
    base_gap_delivery: float,
    base_gap_sla: float,
    round_number: int,
    discount_factor: float = 0.85
) -> dict:
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
    base_gap = abs(target_value - initial_value)
    factor = 1 - (discount_factor ** round_number)
    direction = 1 if target_value > initial_value else -1
    return initial_value + (base_gap * factor * direction)
