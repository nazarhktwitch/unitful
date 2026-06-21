"""Pandas integration for unitful"""

import warnings
from typing import Any


def setup_pandas() -> None:
    """Register the .unitful accessor for pandas Series"""
    try:
        import pandas as pd
    except ImportError:
        warnings.warn("pandas is not installed")
        return

    from .numpy_support import QuantityArray
    from .quantity import Quantity

    @pd.api.extensions.register_series_accessor("unitful")
    class UnitfulAccessor:
        def __init__(self, pandas_obj: pd.Series) -> None:
            self._obj = pandas_obj

        def to(self, unit: Any) -> pd.Series:
            """Convert the series to the given unit and return a new Series of numeric values"""
            import numpy as np
            
            if isinstance(self._obj.values, QuantityArray):
                arr = self._obj.values.to(unit).magnitude
            else:
                # Slow path for object arrays of Quantities
                arr = np.array([
                    q.to(unit).magnitude if isinstance(q, Quantity) else q
                    for q in self._obj
                ])
            return pd.Series(arr, index=self._obj.index, name=self._obj.name)

        def attach(self, unit: Any) -> pd.Series:
            """Attach a unit to a raw numeric Series"""
            # This creates a numpy object array containing Quantity objects
            # which Pandas can store in an object-dtype Series.
            q_list = [Quantity(val, unit) for val in self._obj]
            return pd.Series(q_list, index=self._obj.index, name=self._obj.name, dtype=object)

        @property
        def dimension(self) -> Any:
            """Get the dimension of the first item in the series"""
            if len(self._obj) == 0:
                from .dimension import dimensionless
                return dimensionless
            first = self._obj.iloc[0]
            if isinstance(first, Quantity):
                return first.dimension
            from .dimension import dimensionless
            return dimensionless
