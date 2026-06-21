"""Matplotlib integration for unitful"""

import warnings
from typing import Any


def setup_matplotlib() -> None:
    """Register unitful Quantity and QuantityArray with matplotlib.units"""
    try:
        import matplotlib.units as munits
    except ImportError:
        warnings.warn("matplotlib is not installed")
        return

    from .numpy_support import QuantityArray
    from .quantity import Quantity

    class UnitfulConverter(munits.ConversionInterface):
        @staticmethod
        def axisinfo(unit: Any, axis: Any) -> Any:
            symbol = unit.symbol or unit.name
            # Provide a nicely formatted default label [unit]
            return munits.AxisInfo(label=f"[{symbol}]")  # type: ignore[no-untyped-call]

        @staticmethod
        def default_units(x: Any, axis: Any) -> Any:
            if hasattr(x, "unit"):
                return x.unit
            # If it's a sequence of quantities, get the unit of the first item
            try:
                first = next(iter(x))
                if hasattr(first, "unit"):
                    return first.unit
            except TypeError:
                pass
            return None

        @staticmethod
        def convert(obj: Any, unit: Any, axis: Any) -> Any:
            if isinstance(obj, QuantityArray):
                return obj.to(unit).magnitude
            if isinstance(obj, Quantity):
                return obj.to(unit).magnitude
            
            # Handle sequences (e.g. lists of Quantities)
            if hasattr(obj, '__iter__') and not isinstance(obj, str):
                return [UnitfulConverter.convert(item, unit, axis) for item in obj]
                
            return obj

    converter = UnitfulConverter()
    munits.registry[Quantity] = converter
    munits.registry[QuantityArray] = converter
