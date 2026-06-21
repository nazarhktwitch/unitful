"""JSON and pickle serialization for Quantity"""

from __future__ import annotations

from typing import Any

from .quantity import Quantity
from .registry import registry


def to_json(q: Quantity) -> dict[str, Any]:
    """Serialize a Quantity to a plain dict

    Returns a dict with keys 'value', 'unit', and 'dimensions'
    The 'dimensions' dict maps base dimension symbols to their exponents
    """
    dim = q.unit.dimension
    dims = {k: int(v) if v.denominator == 1 else float(v) for k, v in dim._exponents.items() if v != 0}
    return {
        "value": q.magnitude,
        "unit": q.unit.symbol or q.unit.name,
        "dimensions": dims,
    }


def from_json(d: dict[str, Any]) -> Quantity:
    """Reconstruct a Quantity from a dict produced by to_json

    Only 'value' and 'unit' are required; 'dimensions' is informational
    """
    unit_str: str = d["unit"]
    value: float = float(d["value"])

    try:
        unit = registry.get(unit_str)
    except KeyError:
        raise ValueError(f"Unknown unit {unit_str!r}. Register it first with define_unit().") from None

    return Quantity(value, unit)
