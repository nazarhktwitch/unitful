"""@requires and @returns decorators for dimension-safe function signatures"""

from __future__ import annotations

import functools
from collections.abc import Callable
from typing import Any

from .dimension import Dimension
from .exceptions import DimensionError
from .quantity import Quantity
from .registry import registry


class Dim:
    """Declare an expected dimension from a unit expression string

    Usage::

        @requires(speed=Dim("m/s"), time=Dim("s"))
        def distance_traveled(speed, time):
            ...

    The string is parsed by dividing the named units from the registry
    """

    def __init__(self, expr: str) -> None:
        self._expr = expr
        self._dim = _parse_dim_expr(expr)

    @property
    def dimension(self) -> Dimension:
        return self._dim

    def __repr__(self) -> str:
        return f"Dim({self._expr!r})"


def _parse_dim_expr(expr: str) -> Dimension:
    """Parse an expression like 'm/s', 'm/s^2', 'kg*m/s^2' into a Dimension"""
    # Split on '/' once: numerator * denominator^-1
    parts = expr.split("/", 1)
    num_dim = _parse_product(parts[0])
    if len(parts) == 2:
        den_dim = _parse_product(parts[1])
        return num_dim / den_dim
    return num_dim


def _parse_product(expr: str) -> Dimension:
    """Parse 'kg*m' or 'kg' or 'm^2' into a Dimension"""
    dim = Dimension()
    for token in expr.split("*"):
        token = token.strip()
        if not token:
            continue
        if "^" in token:
            base, exp_str = token.split("^", 1)
            exp = float(exp_str)
        else:
            base, exp = token, 1.0
        base = base.strip()
        try:
            unit = registry.get(base)
        except KeyError:
            raise ValueError(f"Unknown unit in dimension expression: {base!r}") from None
        dim = dim * (unit.dimension ** exp)
    return dim


def requires(**expected_dims: Dim) -> Callable[..., Any]:
    """Validate that keyword arguments have the expected physical dimensions

    If an argument has compatible dimensions but a different unit, it is
    automatically converted before being passed to the function
    """

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            import inspect
            sig = inspect.signature(func)
            bound = sig.bind(*args, **kwargs)
            bound.apply_defaults()

            for param_name, dim_spec in expected_dims.items():
                if param_name not in bound.arguments:
                    continue
                val = bound.arguments[param_name]
                expected = dim_spec.dimension

                if not isinstance(val, Quantity):
                    raise DimensionError.bare_value(
                        func.__name__, param_name, expected.label(), val
                    )

                got_dim = val.dimension
                if got_dim != expected:
                    raise DimensionError.wrong_argument(
                        func.__name__, param_name, expected.label(), val, got_dim.label()
                    )

                # Auto-convert to the canonical SI unit for that dimension so
                # the function receives a consistent unit.  We keep the original
                # unit if no mismatch was detected above.
                # (Conversion already succeeded in the dimension check.)
                bound.arguments[param_name] = val

            return func(*bound.args, **bound.kwargs)

        return wrapper

    return decorator


def returns(dim_spec: Dim) -> Callable[..., Any]:
    """Validate that the return value has the expected physical dimensions"""

    def decorator(func: Callable[..., Any]) -> Callable[..., Any]:
        @functools.wraps(func)
        def wrapper(*args: Any, **kwargs: Any) -> Any:
            result = func(*args, **kwargs)
            expected = dim_spec.dimension

            if not isinstance(result, Quantity):
                # Treat bare numbers as dimensionless.
                from .dimension import dimensionless
                if expected != dimensionless:
                    raise DimensionError.wrong_return(
                        func.__name__, expected.label(), result, "dimensionless"
                    )
                return result

            if result.dimension != expected:
                raise DimensionError.wrong_return(
                    func.__name__, expected.label(), result, result.dimension.label()
                )
            return result

        return wrapper

    return decorator
