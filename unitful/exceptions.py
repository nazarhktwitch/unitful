"""Exceptions raised by unitful"""

from __future__ import annotations


class DimensionError(TypeError):
    """Raised when a dimensional operation is invalid

    Provides a human-readable message describing the mismatch, including the
    values involved and their dimensions
    """

    @classmethod
    def incompatible(
        cls,
        op: str,
        left: object,
        right: object,
        left_dim: str,
        right_dim: str,
    ) -> DimensionError:
        """Mismatch between two operands (e.g. add/subtract)"""
        msg = (
            f"Cannot {op} [{left_dim}] and [{right_dim}]\n"
            f"  left:  {left!r} -> dimensions: {left_dim}\n"
            f"  right: {right!r} -> dimensions: {right_dim}"
        )
        return cls(msg)

    @classmethod
    def wrong_unit(
        cls,
        expected_dim: str,
        got_dim: str,
        got: object,
    ) -> DimensionError:
        """Conversion to an incompatible unit"""
        msg = (
            f"Cannot convert [{got_dim}] to [{expected_dim}]\n"
            f"  value:    {got!r} -> dimensions: {got_dim}\n"
            f"  expected: dimensions: {expected_dim}"
        )
        return cls(msg)

    @classmethod
    def wrong_argument(
        cls,
        func_name: str,
        param: str,
        expected_dim: str,
        got: object,
        got_dim: str,
    ) -> DimensionError:
        """Argument passed to a @requires-decorated function has wrong dimensions"""
        msg = (
            f"Expected [{expected_dim}], got [{got_dim}]\n"
            f"  function:  {func_name}({param}, ...)\n"
            f"  parameter: {param}\n"
            f"  got:       {got!r} -> dimensions: {got_dim}\n"
            f"  expected:  dimensions: {expected_dim}"
        )
        return cls(msg)

    @classmethod
    def bare_value(
        cls,
        func_name: str,
        param: str,
        expected_dim: str,
        got: object,
    ) -> DimensionError:
        """A bare number was passed where a Quantity is required"""
        msg = (
            f"Expected [{expected_dim}], got a bare number\n"
            f"  function:  {func_name}({param}, ...)\n"
            f"  parameter: {param}\n"
            f"  got:       {got!r} (no unit)\n"
            f"  expected:  dimensions: {expected_dim}"
        )
        return cls(msg)

    @classmethod
    def wrong_return(
        cls,
        func_name: str,
        expected_dim: str,
        got: object,
        got_dim: str,
    ) -> DimensionError:
        """Return value of a @returns-decorated function has wrong dimensions"""
        msg = (
            f"Return value has wrong dimensions: expected [{expected_dim}], got [{got_dim}]\n"
            f"  function: {func_name}\n"
            f"  got:      {got!r} -> dimensions: {got_dim}\n"
            f"  expected: dimensions: {expected_dim}"
        )
        return cls(msg)

    @classmethod
    def temperature_arithmetic(cls, op: str) -> DimensionError:
        """Arithmetic on offset temperature units is ambiguous"""
        msg = (
            f"Cannot {op} offset temperature quantities (degC / degF) directly.\n"
            "  Convert to Kelvin first: q.to(K)"
        )
        return cls(msg)
