"""Immutable exponent vector over the 7 SI base quantities"""

from __future__ import annotations

from collections.abc import Iterator
from fractions import Fraction

# Ordered base dimension symbols used throughout the library
BASE_DIMS = ("L", "M", "T", "I", "Theta", "N", "J")

# Human-readable names for error messages
_DIM_NAMES: dict[str, str] = {
    "L": "Length",
    "M": "Mass",
    "T": "Time",
    "I": "Current",
    "Theta": "Temperature",
    "N": "Amount",
    "J": "Luminosity",
}


class Dimension:
    """Immutable vector of rational exponents over the SI base dimensions

    Each position corresponds to L, M, T, I, Theta, N, J in that order
    Arithmetic on Dimension objects implements the algebra of physical dimensions
    """

    __slots__ = ("_exponents",)

    def __init__(self, **exponents: int | float | Fraction) -> None:
        """Create from keyword arguments, e.g. Dimension(L=1, T=-1)"""
        exp: dict[str, Fraction] = {}
        for dim in BASE_DIMS:
            val = exponents.get(dim, 0)
            exp[dim] = Fraction(val).limit_denominator(1000)
        self._exponents: dict[str, Fraction] = exp

    @classmethod
    def _from_dict(cls, d: dict[str, Fraction]) -> Dimension:
        obj = object.__new__(cls)
        obj._exponents = dict(d)
        return obj

    # --- custom dimension support ---

    @classmethod
    def custom(cls, name: str) -> Dimension:
        """Create a dimension with a single non-standard base dimension"""
        obj = object.__new__(cls)
        obj._exponents = {dim: Fraction(0) for dim in BASE_DIMS}
        obj._exponents[name] = Fraction(1)
        return obj

    # --- arithmetic ---

    def __mul__(self, other: Dimension) -> Dimension:
        keys = set(self._exponents) | set(other._exponents)
        result = {k: self._exponents.get(k, Fraction(0)) + other._exponents.get(k, Fraction(0)) for k in keys}
        return Dimension._from_dict(result)

    def __truediv__(self, other: Dimension) -> Dimension:
        keys = set(self._exponents) | set(other._exponents)
        result = {k: self._exponents.get(k, Fraction(0)) - other._exponents.get(k, Fraction(0)) for k in keys}
        return Dimension._from_dict(result)

    def __pow__(self, exp: int | float | Fraction) -> Dimension:
        f = Fraction(exp).limit_denominator(1000)
        result = {k: v * f for k, v in self._exponents.items()}
        return Dimension._from_dict(result)

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Dimension):
            return NotImplemented
        keys = set(self._exponents) | set(other._exponents)
        return all(
            self._exponents.get(k, Fraction(0)) == other._exponents.get(k, Fraction(0))
            for k in keys
        )

    def __hash__(self) -> int:
        return hash(tuple(sorted((k, v) for k, v in self._exponents.items() if v != 0)))

    def is_dimensionless(self) -> bool:
        return all(v == 0 for v in self._exponents.values())

    def keys(self) -> Iterator[str]:
        return iter(self._exponents)

    def __getitem__(self, key: str) -> Fraction:
        return self._exponents.get(key, Fraction(0))

    # --- display ---

    def __str__(self) -> str:
        parts = []
        for k, v in self._exponents.items():
            if v == 0:
                continue
            if v == 1:
                parts.append(k)
            else:
                # Use integer display when possible
                exp_str = str(int(v)) if v.denominator == 1 else str(v)
                parts.append(f"{k}^{exp_str}")
        return "*".join(parts) if parts else "dimensionless"

    def __repr__(self) -> str:
        parts = {k: v for k, v in self._exponents.items() if v != 0}
        return f"Dimension({parts!r})"

    def label(self) -> str:
        """Human-readable label for error messages, e.g. 'Length/Time'"""
        pos = []
        neg = []
        for k, v in self._exponents.items():
            if v == 0:
                continue
            name = _DIM_NAMES.get(k, k)
            if v > 0:
                if v == 1:
                    pos.append(name)
                else:
                    exp_str = str(int(v)) if v.denominator == 1 else str(v)
                    pos.append(f"{name}^{exp_str}")
            else:
                abs_v = -v
                if abs_v == 1:
                    neg.append(name)
                else:
                    exp_str = str(int(abs_v)) if abs_v.denominator == 1 else str(abs_v)
                    neg.append(f"{name}^{exp_str}")
        if not pos and not neg:
            return "dimensionless"
        result = "*".join(pos) if pos else "1"
        if neg:
            result += "/" + "*".join(neg)
        return result

    def si_str(self) -> str:
        """Exponent notation used in error messages, e.g. 'L^1*T^-1'"""
        parts = []
        for k, v in self._exponents.items():
            if v == 0:
                continue
            exp_str = str(int(v)) if v.denominator == 1 else str(v)
            parts.append(f"{k}^{exp_str}")
        return "*".join(parts) if parts else "1"


# Convenience singletons for the 7 SI base dimensions.
dimensionless = Dimension()
Length = Dimension(L=1)
Mass = Dimension(M=1)
Time = Dimension(T=1)
Current = Dimension(I=1)
Temperature = Dimension(Theta=1)
Amount = Dimension(N=1)
Luminosity = Dimension(J=1)
