"""A numeric value with an attached physical unit"""

from __future__ import annotations

import copy
import math
import re
from decimal import Decimal
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

    def __init__(self, value: Any, unit: Unit) -> None:
        self._value = value
        self._unit = unit

    # --- properties ---

    @property
    def magnitude(self) -> Any:
        """Raw numeric value in this quantity's unit"""
        return self._value

    @property
    def unit(self) -> Unit:
        return self._unit

    @property
    def dimension(self) -> Dimension:
        return self._unit.dimension

    # --- SI conversion helpers ---

    def _to_si_value(self) -> Any:
        """Convert value to SI base units (applying offset if any)"""
        if self._unit.is_offset:
            return _add(_mul(self._value, self._unit.scale), self._unit.offset)
        return _mul(self._value, self._unit.scale)

    @classmethod
    def _from_si(cls, si_value: Any, target_unit: Unit) -> Quantity:
        """Build a Quantity from an SI value in the given target unit"""
        if target_unit.is_offset:
            value = _truediv(_sub(si_value, target_unit.offset), target_unit.scale)
        else:
            value = _truediv(si_value, target_unit.scale)
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
        return Quantity(_add(self._value, other_converted._value), self._unit)

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
        return Quantity(_sub(self._value, other_converted._value), self._unit)

    def __mul__(self, other: object) -> Quantity:
        if isinstance(other, Quantity):
            new_dim = self._unit.dimension * other._unit.dimension
            new_scale = self._unit.scale * other._unit.scale
            new_unit = _make_derived_unit(new_dim, new_scale, self._unit, other._unit, "*")
            return Quantity(self._value * other._value, new_unit)
        if isinstance(other, (int, float, Decimal, Fraction)):
            return Quantity(_mul(self._value, other), self._unit)
        return NotImplemented

    def __rmul__(self, other: object) -> Quantity:
        if isinstance(other, (int, float, Decimal, Fraction)):
            return Quantity(_mul(other, self._value), self._unit)
        return NotImplemented

    def __truediv__(self, other: object) -> Quantity:
        if isinstance(other, Quantity):
            new_dim = self._unit.dimension / other._unit.dimension
            new_scale = self._unit.scale / other._unit.scale
            new_unit = _make_derived_unit(new_dim, new_scale, self._unit, other._unit, "/")
            return Quantity(_truediv(self._value, other._value), new_unit)
        if isinstance(other, (int, float, Decimal, Fraction)):
            return Quantity(_truediv(self._value, other), self._unit)
        return NotImplemented

    def __rtruediv__(self, other: object) -> Quantity:
        if isinstance(other, (int, float, Decimal, Fraction)):
            inv_dim = dimensionless / self._unit.dimension
            inv_scale = 1.0 / self._unit.scale
            new_unit = _make_derived_unit(inv_dim, inv_scale, None, self._unit, "1/")
            return Quantity(_truediv(other, self._value), new_unit)
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

    def _cmp_si(self, other: Quantity) -> tuple[Any, Any]:
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
            if type(a) is float or type(b) is float:
                return bool(math.isclose(float(a), float(b), rel_tol=1e-9))
            return bool(a == b)
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
        if type(a) is float or type(b) is float:
            return bool(a <= b or math.isclose(float(a), float(b), rel_tol=1e-9))
        return bool(a <= b)

    def __gt__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        a, b = self._cmp_si(other)
        return a > b

    def __ge__(self, other: object) -> bool:
        if not isinstance(other, Quantity):
            return NotImplemented
        a, b = self._cmp_si(other)
        if type(a) is float or type(b) is float:
            return bool(a >= b or math.isclose(float(a), float(b), rel_tol=1e-9))
        return bool(a >= b)

    def __hash__(self) -> int:
        # Quantities equal after conversion should hash the same
        si = self._to_si_value()
        try:
            return hash((round(float(si), 9), self._unit.dimension))
        except TypeError:
            return hash((si, self._unit.dimension))

    # --- display ---

    def __str__(self) -> str:
        return f"{self._value} {_unit_symbol(self._unit)}"

    def __repr__(self) -> str:
        return f"Quantity({self._value!r}, {_unit_symbol(self._unit)!r})"

    def __format__(self, format_spec: str) -> str:
        return apply_format(float(self._value), _unit_symbol(self._unit), format_spec)

    @classmethod
    def from_string(cls, s: str) -> Quantity:
        from .registry import registry
        match = re.match(r"^([+-]?\d+\.?\d*(?:[eE][+-]?\d+)?(?:/\d+)?)\s*(.*)$", s.strip())
        if not match:
            raise ValueError(f"Cannot parse quantity string: {s!r}")
        num_str, unit_str = match.groups()
        if "/" in num_str and "e" not in num_str.lower():
            num_part, den_part = num_str.split("/", 1)
            value = float(num_part) / float(den_part)
        else:
            value = float(num_str)
            
        unit_str = unit_str.strip()
        if not unit_str:
            from .dimension import dimensionless
            return cls(value, Unit("", "", dimensionless, 1.0))
            
        # Parse expression using eval with registry units
        import ast
        expr = unit_str.replace("^", "**")
        try:
            node = ast.parse(expr, mode='eval')
        except SyntaxError:
            raise ValueError(f"Invalid unit expression: {unit_str!r}")
            
        for n in ast.walk(node):
            if isinstance(n, ast.Call):
                raise ValueError("Function calls not allowed in unit expressions")
                
        safe_locals = {name: Quantity(1.0, u) for name, u in registry._by_name.items()}
        # Also provide symbol lookups for 'm', 's', 'kg'
        safe_locals.update({u.symbol: Quantity(1.0, u) for u in registry._by_name.values() if u.symbol})
        
        unit_qty = eval(compile(node, '<string>', 'eval'), {"__builtins__": {}}, safe_locals)
        if not isinstance(unit_qty, Quantity):
            raise ValueError(f"Invalid unit expression: {unit_str!r}")
            
        return cls(_mul(value, unit_qty.magnitude), unit_qty.unit)

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

def _mul(a: Any, b: Any) -> Any:
    try:
        if isinstance(a, Fraction) and isinstance(b, float) and b.is_integer():
            return a * int(b)
        if isinstance(b, Fraction) and isinstance(a, float) and a.is_integer():
            return int(a) * b
        return a * b
    except TypeError:
        if isinstance(a, Decimal):
            return a * Decimal(str(b))
        if isinstance(b, Decimal):
            return Decimal(str(a)) * b
        raise

def _truediv(a: Any, b: Any) -> Any:
    try:
        if isinstance(a, Fraction) and isinstance(b, float) and b.is_integer():
            return a / int(b)
        if isinstance(b, Fraction) and isinstance(a, float) and a.is_integer():
            return int(a) / b
        return a / b
    except TypeError:
        if isinstance(a, Decimal):
            return a / Decimal(str(b))
        if isinstance(b, Decimal):
            return Decimal(str(a)) / b
        raise

def _add(a: Any, b: Any) -> Any:
    try:
        return a + b
    except TypeError:
        if isinstance(a, Decimal):
            return a + Decimal(str(b))
        if isinstance(b, Decimal):
            return Decimal(str(a)) + b
        raise

def _sub(a: Any, b: Any) -> Any:
    try:
        return a - b
    except TypeError:
        if isinstance(a, Decimal):
            return a - Decimal(str(b))
        if isinstance(b, Decimal):
            return Decimal(str(a)) - b
        raise
