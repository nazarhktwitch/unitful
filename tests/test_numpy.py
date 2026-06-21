"""Tests for NumPy integration (QuantityArray)"""

import math
import pytest

try:
    import numpy as np
except BaseException:
    pytest.skip("numpy is not available or crashes on import", allow_module_level=True)

from unitful import (
    m, kg, s,
    DimensionError,
    Quantity,
)
from unitful.numpy_support import QuantityArray


# ---------------------------------------------------------------------------
# Construction
# ---------------------------------------------------------------------------

def test_from_ndarray_mul():
    arr = np.array([1.70, 1.85, 1.92]) * m
    assert isinstance(arr, QuantityArray)
    assert arr.unit.symbol == "m"
    assert arr.shape == (3,)


def test_magnitude_property():
    arr = np.array([1.0, 2.0, 3.0]) * m
    np.testing.assert_array_almost_equal(arr.magnitude, [1.0, 2.0, 3.0])


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------

def test_to_compatible():
    from unitful import km
    arr = np.array([1000.0, 2000.0]) * m
    result = arr.to(km)
    assert isinstance(result, QuantityArray)
    np.testing.assert_array_almost_equal(result.magnitude, [1.0, 2.0])


def test_to_incompatible_raises():
    arr = np.array([1.0, 2.0]) * m
    with pytest.raises(DimensionError):
        arr.to(kg)


# ---------------------------------------------------------------------------
# Arithmetic
# ---------------------------------------------------------------------------

def test_mul_scalar():
    arr = np.array([1.0, 2.0, 3.0]) * m
    result = arr * 2
    np.testing.assert_array_almost_equal(result.magnitude, [2.0, 4.0, 6.0])


def test_div_scalar():
    arr = np.array([10.0, 20.0]) * m
    result = arr / 2
    np.testing.assert_array_almost_equal(result.magnitude, [5.0, 10.0])


def test_mul_quantity():
    lengths = np.array([3.0, 4.0]) * m
    result = lengths * (2 * m)
    from unitful.dimension import Dimension
    assert result.dimension == Dimension(L=2)


def test_div_quantity_arrays():
    weights = np.array([70.0, 90.0, 85.0]) * kg
    heights = np.array([1.70, 1.85, 1.92]) * m
    bmi = weights / heights ** 2
    assert isinstance(bmi, QuantityArray)
    from unitful.dimension import Dimension
    assert bmi.dimension == Dimension(M=1, L=-2)


def test_pow():
    arr = np.array([2.0, 3.0]) * m
    result = arr ** 2
    from unitful.dimension import Dimension
    assert result.dimension == Dimension(L=2)
    np.testing.assert_array_almost_equal(result.magnitude, [4.0, 9.0])


def test_add_same_unit():
    a = np.array([1.0, 2.0]) * m
    b = np.array([3.0, 4.0]) * m
    result = a + b
    np.testing.assert_array_almost_equal(result.magnitude, [4.0, 6.0])


def test_add_incompatible_raises():
    a = np.array([1.0]) * m
    b = np.array([1.0]) * kg
    with pytest.raises(DimensionError):
        _ = a + b


# ---------------------------------------------------------------------------
# numpy reductions
# ---------------------------------------------------------------------------

def test_np_mean():
    arr = np.array([1.0, 2.0, 3.0]) * m
    result = np.mean(arr)
    assert isinstance(result, Quantity)
    assert math.isclose(result.magnitude, 2.0)
    assert result.unit.symbol == "m"


def test_np_sum():
    arr = np.array([1.0, 2.0, 3.0]) * m
    result = np.sum(arr)
    assert isinstance(result, Quantity)
    assert math.isclose(result.magnitude, 6.0)


def test_np_std():
    arr = np.array([1.0, 2.0, 3.0]) * m
    result = np.std(arr)
    assert isinstance(result, Quantity)
    assert result.unit.symbol == "m"


def test_np_min():
    arr = np.array([3.0, 1.0, 2.0]) * m
    result = np.min(arr)
    assert isinstance(result, Quantity)
    assert math.isclose(result.magnitude, 1.0)


def test_np_max():
    arr = np.array([3.0, 1.0, 2.0]) * m
    result = np.max(arr)
    assert isinstance(result, Quantity)
    assert math.isclose(result.magnitude, 3.0)


# ---------------------------------------------------------------------------
# Indexing
# ---------------------------------------------------------------------------

def test_single_index_returns_quantity():
    arr = np.array([1.0, 2.0, 3.0]) * m
    item = arr[0]
    assert isinstance(item, Quantity)
    assert math.isclose(item.magnitude, 1.0)


def test_slice_returns_quantity_array():
    arr = np.array([1.0, 2.0, 3.0]) * m
    sliced = arr[1:]
    assert isinstance(sliced, QuantityArray)


# ---------------------------------------------------------------------------
# Repr / str
# ---------------------------------------------------------------------------

def test_repr():
    arr = np.array([1.0]) * m
    assert "QuantityArray" in repr(arr)


def test_str():
    arr = np.array([1.0]) * m
    assert "m" in str(arr)
