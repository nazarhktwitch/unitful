"""Tests for Quantity arithmetic, conversion, and formatting"""

import copy
import math
import pickle
import pytest

from unitful import (
    Quantity,
    DimensionError,
    m, km, cm, s, h, kg, g,
    K, degC, degF,
    N, J, W, Pa,
)
from unitful.registry import Unit
from unitful.dimension import Dimension


# ---------------------------------------------------------------------------
# Construction helpers
# ---------------------------------------------------------------------------

def test_magnitude():
    q = 5.0 * m
    assert q.magnitude == 5.0


def test_unit_property():
    q = 3 * kg
    assert q.unit.name == "kg"


def test_dimension_property():
    q = 3 * kg
    assert q.dimension == Dimension(M=1)


# ---------------------------------------------------------------------------
# Arithmetic
# ---------------------------------------------------------------------------

def test_add_same_unit():
    result = (2 * m) + (3 * m)
    assert math.isclose(result.magnitude, 5.0)
    assert result.unit.symbol == "m"


def test_add_different_compatible_unit():
    result = (1 * km) + (500 * m)
    # 1 km + 500 m = 1.5 km (result stays in left unit)
    assert math.isclose(result.magnitude, 1.5, rel_tol=1e-9)


def test_add_incompatible_raises():
    with pytest.raises(DimensionError):
        _ = (1 * m) + (1 * s)


def test_radd_zero():
    q = 2 * m
    assert sum([1 * m, 1 * m]) == 2 * m


def test_sub_same_unit():
    result = (5 * m) - (2 * m)
    assert math.isclose(result.magnitude, 3.0)


def test_sub_incompatible_raises():
    with pytest.raises(DimensionError):
        _ = (1 * m) - (1 * kg)


def test_mul_scalar():
    result = 3 * (2 * m)
    assert math.isclose(result.magnitude, 6.0)


def test_mul_scalar_right():
    result = (2 * m) * 3
    assert math.isclose(result.magnitude, 6.0)


def test_mul_quantities():
    force = (2 * kg) * (3 * m / s ** 2)
    assert force.dimension == Dimension(M=1, L=1, T=-2)
    assert math.isclose(force.magnitude, 6.0)


def test_div_scalar():
    result = (10 * m) / 2
    assert math.isclose(result.magnitude, 5.0)


def test_div_quantities():
    speed = (100 * m) / (10 * s)
    assert speed.dimension == Dimension(L=1, T=-1)
    assert math.isclose(speed.magnitude, 10.0)


def test_rtruediv():
    inv = 1 / (2 * s)
    assert inv.dimension == Dimension(T=-1)
    assert math.isclose(inv.magnitude, 0.5)


def test_pow_integer():
    area = (3 * m) ** 2
    assert area.dimension == Dimension(L=2)
    assert math.isclose(area.magnitude, 9.0)


def test_neg():
    q = -(5 * m)
    assert q.magnitude == -5.0


def test_pos():
    q = +(5 * m)
    assert q.magnitude == 5.0


def test_abs():
    q = abs(-5 * m)
    assert q.magnitude == 5.0


# ---------------------------------------------------------------------------
# Conversion
# ---------------------------------------------------------------------------

def test_to_compatible():
    speed = (100 * m) / (1 * s)
    result = speed.to(km / h)
    assert math.isclose(result.magnitude, 360.0, rel_tol=1e-6)


def test_to_incompatible_raises():
    with pytest.raises(DimensionError):
        _ = (1 * m).to(kg)


def test_to_accepts_unit_object():
    q = 1000 * m
    result = q.to(km.unit)
    assert math.isclose(result.magnitude, 1.0, rel_tol=1e-9)


def test_km_to_m():
    q = 1 * km
    result = q.to(m)
    assert math.isclose(result.magnitude, 1000.0)


def test_degc_to_k():
    q = 0 * degC
    result = q.to(K)
    assert math.isclose(result.magnitude, 273.15, rel_tol=1e-6)


def test_degf_to_k():
    q = 32 * degF
    result = q.to(K)
    assert math.isclose(result.magnitude, 273.15, rel_tol=1e-6)


def test_k_to_degc():
    q = 373.15 * K
    result = q.to(degC)
    assert math.isclose(result.magnitude, 100.0, rel_tol=1e-6)


def test_degc_to_degf():
    q = 100 * degC
    result = q.to(degF)
    assert math.isclose(result.magnitude, 212.0, rel_tol=1e-6)


# ---------------------------------------------------------------------------
# Temperature DimensionError
# ---------------------------------------------------------------------------

def test_add_degc_raises():
    with pytest.raises(DimensionError):
        _ = (5 * degC) + (3 * degC)


def test_sub_degc_raises():
    with pytest.raises(DimensionError):
        _ = (5 * degC) - (3 * degC)


# ---------------------------------------------------------------------------
# Comparisons
# ---------------------------------------------------------------------------

def test_eq_same_unit():
    assert (1 * m) == (1 * m)


def test_eq_different_unit():
    assert (1 * km) == (1000 * m)


def test_lt():
    assert (1 * m) < (2 * m)


def test_le():
    assert (1 * m) <= (1 * m)
    assert (1 * m) <= (2 * m)


def test_gt():
    assert (2 * m) > (1 * m)


def test_ge():
    assert (2 * m) >= (1 * m)
    assert (2 * m) >= (2 * m)


def test_eq_incompatible_is_false():
    assert not ((1 * m) == (1 * kg))


def test_lt_incompatible_raises():
    with pytest.raises(DimensionError):
        _ = (1 * m) < (1 * kg)


# ---------------------------------------------------------------------------
# Formatting
# ---------------------------------------------------------------------------

def test_str():
    q = 100.0 * m
    assert str(q) == "100.0 m"


def test_repr():
    q = 100.0 * m
    assert "Quantity" in repr(q)
    assert "100.0" in repr(q)


def test_format_plain():
    q = 100.0 * m
    assert format(q, ".1f") == "100.0 m"


def test_format_unicode():
    q = 9.461e15 * m
    result = format(q, ".2e~P")
    # Should contain Unicode superscripts or x
    assert "m" in result


def test_format_latex():
    q = 9.461e15 * m
    result = format(q, ".2e~L")
    assert r"\mathrm" in result or "mathrm" in result


def test_format_html():
    q = 9.461e15 * m
    result = format(q, ".2e~H")
    assert "<span>" in result
    assert "</span>" in result


def test_fstring():
    q = 100.0 * m
    assert f"{q:.2f}" == "100.00 m"


# ---------------------------------------------------------------------------
# Pickle and copy
# ---------------------------------------------------------------------------

def test_pickle_roundtrip():
    q = 42.5 * m
    restored = pickle.loads(pickle.dumps(q))
    assert restored == q
    assert restored.unit.symbol == q.unit.symbol


def test_copy():
    q = 42.5 * m
    c = copy.copy(q)
    assert c == q


def test_deepcopy():
    q = 42.5 * m
    c = copy.deepcopy(q)
    assert c == q


# ---------------------------------------------------------------------------
# Error messages
# ---------------------------------------------------------------------------

def test_dimension_error_message_contains_dims():
    with pytest.raises(DimensionError) as exc_info:
        _ = (1 * m) + (1 * s)
    msg = str(exc_info.value)
    assert "Length" in msg or "L" in msg
    assert "Time" in msg or "T" in msg


def test_to_error_message():
    with pytest.raises(DimensionError) as exc_info:
        (1 * m).to(kg)
    msg = str(exc_info.value)
    assert "Length" in msg or "Mass" in msg
