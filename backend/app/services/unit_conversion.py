from __future__ import annotations

import re

WEIGHT_TO_GRAMS = {
    "g": 1.0,
    "kg": 1000.0,
    "lb": 453.592,
    "oz": 28.3495,
}

VOLUME_TO_ML = {
    "ml": 1.0,
    "l": 1000.0,
}


def compute_price_per_100g(price: float, weight_value: float | None, weight_unit: str | None) -> float | None:
    if weight_value is None or weight_unit is None or weight_value <= 0:
        return None

    unit_lower = weight_unit.lower()

    if unit_lower in WEIGHT_TO_GRAMS:
        grams = weight_value * WEIGHT_TO_GRAMS[unit_lower]
        return round(price / grams * 100, 2)

    if unit_lower in VOLUME_TO_ML:
        ml = weight_value * VOLUME_TO_ML[unit_lower]
        return round(price / ml * 100, 2)

    return None


def parse_unit_string(unit_str: str) -> tuple[float | None, str | None]:
    if not unit_str:
        return None, None

    unit_str = unit_str.strip()

    # Match patterns like "454g", "2L", "1.75L", "750ml", "1kg"
    match = re.match(r"^(\d+\.?\d*)\s*(g|kg|lb|oz|ml|l)$", unit_str, re.IGNORECASE)
    if match:
        return float(match.group(1)), match.group(2).lower()

    # Match "per kg", "per lb"
    match = re.match(r"^per\s+(g|kg|lb|oz|ml|l)$", unit_str, re.IGNORECASE)
    if match:
        return 1.0, match.group(1).lower()

    # Match "10lb bag" style
    match = re.match(r"^(\d+\.?\d*)\s*(g|kg|lb|oz|ml|l)\b", unit_str, re.IGNORECASE)
    if match:
        return float(match.group(1)), match.group(2).lower()

    # Count-based items: "each", "6 pack", "12 pack", etc.
    return None, None
