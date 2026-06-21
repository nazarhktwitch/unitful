"""NumPy integration: QuantityArray and ufunc hooks"""

from __future__ import annotations

try:
    import numpy as np
    _NUMPY = True
except BaseException:
    _NUMPY = False
    np = None  # type: ignore[assignment]

from .dimension import Dimension
from .exceptions import DimensionError
from .quantity import Quantity
from .registry import Unit


class QuantityArray:
    """A NumPy array with an attached physical unit

    Wraps an `ndarray` rather than subclassing it, to avoid subclass pitfalls
    All element-wise ufuncs that preserve shape are supported via `__array_ufunc__`
    """

    def __init__(self, array: np.ndarray, unit: Unit) -> None:
        if not _NUMPY:
            raise ImportError("numpy is required for QuantityArray")
        self._array = np.asarray(array, dtype=float)
        self._unit = unit

    # --- properties ---

    @property
    def magnitude(self) -> np.ndarray:
        return self._array

    @property
    def unit(self) -> Unit:
        return self._unit

    @property
    def dimension(self) -> Dimension:
        return self._unit.dimension

    @property
    def shape(self) -> tuple:
        return self._array.shape

    @property
    def dtype(self):
        return self._array.dtype

    def __len__(self) -> int:
        return len(self._array)

    # --- conversion ---

    def to(self, target: Quantity | Unit) -> QuantityArray:
        """Convert to a different unit, returning a new QuantityArray"""
        if isinstance(target, Quantity):
            target_unit = target._unit
        elif isinstance(target, Unit):
            target_unit = target
        else:
            raise TypeError(f"Expected Quantity or Unit, got {type(target).__name__!r}")

        if self._unit.dimension != target_unit.dimension:
            raise DimensionError.wrong_unit(
                target_unit.dimension.label(),
                self._unit.dimension.label(),
                self,
            )

        if self._unit.is_offset or target_unit.is_offset:
            si = self._array * self._unit.scale + self._unit.offset
            new_arr = (si - target_unit.offset) / target_unit.scale
        else:
            new_arr = self._array * (self._unit.scale / target_unit.scale)
        return QuantityArray(new_arr, target_unit)

    # --- arithmetic ---

    def __mul__(self, other: object) -> QuantityArray | Quantity:
        if isinstance(other, (int, float)):
            return QuantityArray(self._array * other, self._unit)
        if isinstance(other, Quantity):
            from .quantity import _make_derived_unit
            new_dim = self._unit.dimension * other._unit.dimension
            new_scale = self._unit.scale * other._unit.scale
            new_unit = _make_derived_unit(new_dim, new_scale, self._unit, other._unit, "*")
            return QuantityArray(self._array * other._value, new_unit)
        if isinstance(other, QuantityArray):
            from .quantity import _make_derived_unit
            new_dim = self._unit.dimension * other._unit.dimension
            new_scale = self._unit.scale * other._unit.scale
            new_unit = _make_derived_unit(new_dim, new_scale, self._unit, other._unit, "*")
            return QuantityArray(self._array * other._array, new_unit)
        return NotImplemented

    def __rmul__(self, other: object) -> QuantityArray:
        if isinstance(other, (int, float)):
            return QuantityArray(other * self._array, self._unit)
        return NotImplemented

    def __truediv__(self, other: object) -> QuantityArray:
        if isinstance(other, (int, float)):
            return QuantityArray(self._array / other, self._unit)
        if isinstance(other, Quantity):
            from .quantity import _make_derived_unit
            new_dim = self._unit.dimension / other._unit.dimension
            new_scale = self._unit.scale / other._unit.scale
            new_unit = _make_derived_unit(new_dim, new_scale, self._unit, other._unit, "/")
            return QuantityArray(self._array / other._value, new_unit)
        if isinstance(other, QuantityArray):
            from .quantity import _make_derived_unit
            new_dim = self._unit.dimension / other._unit.dimension
            new_scale = self._unit.scale / other._unit.scale
            new_unit = _make_derived_unit(new_dim, new_scale, self._unit, other._unit, "/")
            return QuantityArray(self._array / other._array, new_unit)
        return NotImplemented

    def __pow__(self, exp: int | float) -> QuantityArray:
        new_dim = self._unit.dimension ** exp
        new_scale = self._unit.scale ** exp
        sym = f"{self._unit.symbol}^{exp}"
        new_unit = Unit(name=sym, symbol=sym, dimension=new_dim, scale=new_scale)
        return QuantityArray(self._array ** exp, new_unit)

    def __add__(self, other: object) -> QuantityArray:
        if isinstance(other, QuantityArray):
            if self._unit.dimension != other._unit.dimension:
                raise DimensionError.incompatible(
                    "add", self, other,
                    self._unit.dimension.label(), other._unit.dimension.label(),
                )
            other_arr = other.to(self._unit)._array
            return QuantityArray(self._array + other_arr, self._unit)
        return NotImplemented

    def __sub__(self, other: object) -> QuantityArray:
        if isinstance(other, QuantityArray):
            if self._unit.dimension != other._unit.dimension:
                raise DimensionError.incompatible(
                    "subtract", self, other,
                    self._unit.dimension.label(), other._unit.dimension.label(),
                )
            other_arr = other.to(self._unit)._array
            return QuantityArray(self._array - other_arr, self._unit)
        return NotImplemented

    # --- numpy protocol ---

    def __array__(self, dtype=None, copy=None):
        if dtype is not None:
            return self._array.astype(dtype)
        return self._array

    def __array_ufunc__(self, ufunc, method, *inputs, **kwargs):
        return _quantity_ufunc(ufunc, method, inputs, kwargs)

    def __array_function__(self, func, types, args, kwargs):
        return _quantity_function(func, types, args, kwargs)

    def __repr__(self) -> str:
        return f"QuantityArray({self._array!r}, unit={self._unit.symbol!r})"

    def __str__(self) -> str:
        return f"{self._array} {self._unit.symbol}"

    def __getitem__(self, idx):
        import numpy as _np
        val = self._array[idx]
        if _np.ndim(val) == 0:
            return Quantity(float(val), self._unit)
        return QuantityArray(val, self._unit)


# ---------------------------------------------------------------------------
# ufunc dispatch
# ---------------------------------------------------------------------------

def _quantity_ufunc(ufunc, method, inputs, kwargs):
    """Handle numpy ufuncs applied to Quantity or QuantityArray objects"""
    if not _NUMPY:
        return NotImplemented

    # Unwrap all inputs to raw arrays/scalars and collect units
    raw_inputs = []
    units = []
    for inp in inputs:
        if isinstance(inp, QuantityArray):
            raw_inputs.append(inp._array)
            units.append(inp._unit)
        elif isinstance(inp, Quantity):
            raw_inputs.append(inp._value)
            units.append(inp._unit)
        else:
            raw_inputs.append(inp)
            units.append(None)

    result = getattr(ufunc, method)(*raw_inputs, **kwargs)

    # Determine result unit based on ufunc type
    if ufunc in (np.add, np.subtract):
        # Both operands must have compatible dimensions
        q_units = [u for u in units if u is not None]
        if len(q_units) >= 2 and q_units[0].dimension != q_units[1].dimension:
            raise DimensionError.incompatible(
                ufunc.__name__, inputs[0], inputs[1],
                q_units[0].dimension.label(), q_units[1].dimension.label(),
            )
        out_unit = q_units[0] if q_units else None

    elif ufunc is np.multiply:
        q_units = [u for u in units if u is not None]
        if len(q_units) == 2:
            from .quantity import _make_derived_unit
            new_dim = q_units[0].dimension * q_units[1].dimension
            new_scale = q_units[0].scale * q_units[1].scale
            out_unit = _make_derived_unit(new_dim, new_scale, q_units[0], q_units[1], "*")
        elif len(q_units) == 1:
            out_unit = q_units[0]
        else:
            out_unit = None

    elif ufunc is np.true_divide:
        q_units = [u for u in units if u is not None]
        if len(q_units) == 2:
            from .quantity import _make_derived_unit
            new_dim = q_units[0].dimension / q_units[1].dimension
            new_scale = q_units[0].scale / q_units[1].scale
            out_unit = _make_derived_unit(new_dim, new_scale, q_units[0], q_units[1], "/")
        elif len(q_units) == 1:
            out_unit = q_units[0]
        else:
            out_unit = None

    elif ufunc is np.power:
        if units[0] is not None:
            exp = raw_inputs[1]
            new_dim = units[0].dimension ** exp
            new_scale = units[0].scale ** exp
            sym = f"{units[0].symbol}^{exp}"
            out_unit = Unit(name=sym, symbol=sym, dimension=new_dim, scale=new_scale)
        else:
            out_unit = None

    elif ufunc in (np.sqrt,):
        if units[0] is not None:
            new_dim = units[0].dimension ** 0.5
            new_scale = units[0].scale ** 0.5
            sym = f"{units[0].symbol}^0.5"
            out_unit = Unit(name=sym, symbol=sym, dimension=new_dim, scale=new_scale)
        else:
            out_unit = None

    else:
        # For unhandled ufuncs, strip units and return raw array
        out_unit = units[0] if units else None

    if out_unit is None:
        return result

    if np.ndim(result) == 0:
        return Quantity(float(result), out_unit)
    return QuantityArray(result, out_unit)


# ---------------------------------------------------------------------------
# numpy function dispatch (np.mean, np.sum, etc.)
# ---------------------------------------------------------------------------

def _quantity_function(func, types, args, kwargs):
    """Handle numpy functions that reduce or transform QuantityArray"""
    if not _NUMPY:
        return NotImplemented

    if func is np.mean:
        arr = args[0]
        result = np.mean(arr._array, **kwargs)
        if np.ndim(result) == 0:
            return Quantity(float(result), arr._unit)
        return QuantityArray(result, arr._unit)

    if func is np.sum:
        arr = args[0]
        result = np.sum(arr._array, **kwargs)
        if np.ndim(result) == 0:
            return Quantity(float(result), arr._unit)
        return QuantityArray(result, arr._unit)

    if func is np.std:
        arr = args[0]
        result = np.std(arr._array, **kwargs)
        if np.ndim(result) == 0:
            return Quantity(float(result), arr._unit)
        return QuantityArray(result, arr._unit)

    if func is np.min or func is np.amin:
        arr = args[0]
        result = np.min(arr._array, **kwargs)
        if np.ndim(result) == 0:
            return Quantity(float(result), arr._unit)
        return QuantityArray(result, arr._unit)

    if func is np.max or func is np.amax:
        arr = args[0]
        result = np.max(arr._array, **kwargs)
        if np.ndim(result) == 0:
            return Quantity(float(result), arr._unit)
        return QuantityArray(result, arr._unit)

    return NotImplemented
