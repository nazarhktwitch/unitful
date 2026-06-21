"""A numeric value with an attached physical unit"""

from __future__ import annotations

import copy
import math
from fractions import Fraction
from typing import TYPE_CHECKING, Any

from .dimension import Dimension, dimensionless
from .exceptions import DimensionError
from .formatting import apply_format
from .registry import Unit

if TYPE_CHECKING:
    pass

# Names of offset temperature units (these require special handling)
_OFFSET_UNITS = {"degC", "degF"}
_KELVIN_SCALE = 1.0  # K has scale=1, offset=0 by definition


def _unit_symbol(unit: Unit) -> str:
    """Build a display string for a unit derived from arithmetic"""
    return unit.symbol or unit.name


class Quantity:
    """A scalar numeric value with a physical unit

    Arithmetic operators propagate units and raise DimensionError on
    incompatible operations (e.g. adding Length to Time)
    """

    __slots__ = ("_value", "_unit")

    def __init__(self, value: float, unit: Unit) -> None:
        self._value = float(value)
        self._unit = unit

    # --- properties ---

    @property
    def magnitude(self) -> float:
        """Raw numeric value in this quantity's unit"""
        return self._value

    @property
    def unit(self) -> Unit:
        return self._unit

    @property
    def dimension(self) -> Dimension:
        return self._unit.dimension

    # --- SI conversion helpers ---

    def _to_si_value(self) -> float:
        """Convert value to SI base units (applying offset if any)"""
        if self._unit.is_offset:
            return self._value * self._unit.scale + self._unit.offset
        return self._value * self._unit.scale

    @classmethod
    def _from_si(cls, si_value: float, target_unit: Unit) -> Quantity:
        """Build a Quantity from an SI value in the given target unit"""
        if target_unit.is_offset:
            value = (si_value - target_unit.offset) / target_unit.scale
        else:
            value = si_value / target_unit.scale
        return cls(value, target_unit)

    # --- conversion ---

    def to(self, target: Quantity | Unit) -> Quantity:
        """Convert to a different unit

        Accepts either a unit Quantity (e.g. `q.to(km/h)`) or a Unit object
        """
        if isinstance(target, Quantity):
            target_unit = target._unit
        elif isinstance(target, Unit):
            target_unit = target
        else:
            raise TypeError(f"Expected a Quantity or Unit, got {type(target).__name__!r}")

        if self._unit.dimension != target_unit.dimension:
            raise DimensionError.wrong_unit(
                target_unit.dimension.label(),
                self._unit.dimension.label(),
                self,
            )

        # Offset units: go through SI kelvin as intermediate
        si_val = self._to_si_value()
        return Quantity._from_si(si_val, target_unit)

    # --- arithmetic ---

    def _check_offset(self, op: str) -> None:
        if self._unit.is_offset:
            raise DimensionError.temperature_arithmetic(op)

    def __add__(self, other: object) -> Quantity:
        if not isinstance(other, Quantity):
            return NotImplemented
        self._check_offset("add")
        other._check_offset("add")
        if self._unit.dimension != other._unit.dimension:
            raise DimensionError.incompatible(
                "add",
                self, other,
                self._unit.dimension.label(),
                other._unit.dimension.label(),
            )
        # Convert other to self's unit
        other_converted = other.to(self._unit)
        return Quantity(self._value + other_converted._value, self._unit)

    def __radd__(self, other: object) -> Quantity:
        if other == 0:
            return self
        return NotImplemented

    def __sub__(self, other: object) -> Quantity:
        if not isinstance(other, Quantity):
            return NotImplemented
        self._check_offset("subtract")
        other._check_offset("subtract")
        if self._unit.dimension != other._unit.dimension:
            raise DimensionError.incompatible(
                "subtract",
                self, other,
                self._unit.dimension.label(),
                other._unit.dimension.label(),
            )
        other_converted = other.to(self._unit)
        return Quantity(self._value - other_converted._value, self._unit)

    def __mul__(self, other: object) -> Quantity:
        if isinstance(other, Quantity):
            new_dim = self._unit.dimension * other._unit.dimension
            new_scale = self._unit.scale * other._unit.scale
            new_unit = _make_derived_unit(new_dim, new_scale, self._unit, other._unit, "*")
            return Quantity(self._value * other._value, new_unit)
        if isinstance(other, (int, float)):
            return Quantity(self._value * other, self._unit)
        return NotImplemented

    def __rmul__(self, other: object) -> Quantity:
        if isinstance(other, (int, float)):
            return Quantity(other * self._value, self._unit)
        return NotImplemented

    def __truediv__(self, other: object) -> Quantity:
        if isinstance(other, Quantity):
            new_dim = self._unit.dimension / other._unit.dimension
            new_scale = self._unit.scale / other._unit.scale
            new_unit = _make_derived_unit(new_dim, new_scale, self._unit, other._unit, "/")
            return Quantity(self._value / other._value, new_unit)
        if isinstance(other, (int, float)):
            return Quantity(self._value / other, self._unit)
        return NotImplemented

    def __rtruediv__(self, other: object) -> Quantity:
        if isinstance(other, (int, float)):
            inv_dim = dimensionless / self._unit.dimension
            inv_scale = 1.0 / self._unit.scale
            new_unit = _make_derived_unit(inv_dim, inv_scale, None, self._unit, "1/")
            return Quantity(other / self._value, new_unit)
        return NotImplemented

    def __pow__(self, exp: int | float | Fraction) -> Quantity:
        new_dim = self._unit.dimension ** exp
        new_scale = self._unit.scale ** exp
        sym = f"{self._unit.symbol}^{exp}" if exp != 1 else self._unit.symbol
        new_unit = Unit(
            name=sym,
            symbol=sym,
            dimension=new_dim,
            scale=new_scale,
        )
        return Quantity(self._value ** exp, new_unit)

    def __neg__(self) -> Quantity:
        return Quantity(-self._value, self._unit)

    def __pos__(self) -> Quantity:
        return Quantity(self._value, self._unit)

    def __abs__(self) -> Quantity:
        return Quantity(abs(self._value), self._unit)

    # --- comparisons ---

    def _cmp_si(self, other: Quantity) -> tuple[float, float]:
        if self._unit.dimension != other._unit.dimension:
            raise DimensionError.incompatible(
                "compare",
                self, other,
                self._unit.dimension.label(),
                other._unit.dimension.label(),
            )
        return self._to_si_value(), other._to_si_value()

    def __eq__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        try:
            a, b = self._cmp_si(other)
            return math.isclose(a, b, rel_tol=1e-9)
        except DimensionError:
            return False

    def __lt__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        a, b = self._cmp_si(other)
        return a < b

    def __le__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        a, b = self._cmp_si(other)
        return a <= b or math.isclose(a, b, rel_tol=1e-9)

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        a, b = self._cmp_si(other)
        return a > b

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        a, b = self._cmp_si(other)
        return a >= b or math.isclose(a, b, rel_tol=1e-9)

    def __hash__(self) -> int:
        # Quantities equal after conversion should hash the same
        si = self._to_si_value()
        return hash((round(si, 9), self._unit.dimension))

    # --- display ---

    def __str__(self) -> str:
        return f"{self._value} {_unit_symbol(self._unit)}"

    def __repr__(self) -> str:
        return f"Quantity({self._value!r}, {_unit_symbol(self._unit)!r})"

    def __format__(self, format_spec: str) -> str:
        return apply_format(self._value, _unit_symbol(self._unit), format_spec)

    # --- pickle / copy ---

    def __reduce__(self) -> tuple[Any, Any]:
        return (_rebuild_quantity, (self._value, self._unit))

    def __copy__(self) -> Quantity:
        return Quantity(self._value, self._unit)

    def __deepcopy__(self, memo: dict[int, Any]) -> Quantity:
        return Quantity(copy.deepcopy(self._value, memo), self._unit)

    # --- numpy protocol ---

    def __array__(self, dtype: Any = None, copy: Any = None) -> Any:
        import numpy as np
        arr = np.array([self._value], dtype=dtype)
        return arr

    def __array_ufunc__(self, ufunc: Any, method: Any, *inputs: Any, **kwargs: Any) -> Any:
        # Delegate to QuantityArray when numpy tries to use a ufunc on a Quantity
        from .numpy_support import _quantity_ufunc
        return _quantity_ufunc(ufunc, method, inputs, kwargs)  # type: ignore[no-untyped-call]


def _rebuild_quantity(value: float, unit: Unit) -> Quantity:
    return Quantity(value, unit)


def _make_derived_unit(
    dim: Dimension,
    scale: float,
    left: Unit | None,
    right: Unit,
    op: str,
) -> Unit:
    """Build a synthetic Unit for the result of an arithmetic operation"""
    if op == "*" and left is not None:
        sym = f"{left.symbol}*{right.symbol}"
        name = sym
    elif op == "/" and left is not None:
        sym = f"{left.symbol}/{right.symbol}"
        name = sym
    elif op == "1/":
        sym = f"1/{right.symbol}"
        name = sym
    else:
        sym = ""
        name = ""
    return Unit(name=name, symbol=sym, dimension=dim, scale=scale)
