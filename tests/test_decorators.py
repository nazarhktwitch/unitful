"""Tests for @requires and @returns decorators"""

import math
import pytest

from unitful import (
    requires, returns, Dim,
    DimensionError,
    m, s, kg, km, h,
)


# ---------------------------------------------------------------------------
# @requires
# ---------------------------------------------------------------------------

@requires(speed=Dim("m/s"), time=Dim("s"))
def distance_traveled(speed, time):
    return speed * time


def test_requires_correct_args():
    result = distance_traveled(10 * m / s, 5 * s)
    assert math.isclose(result.magnitude, 50.0)


def test_requires_wrong_dimension_raises():
    with pytest.raises(DimensionError) as exc_info:
        distance_traveled(10 * kg, 5 * s)
    msg = str(exc_info.value)
    assert "speed" in msg
    assert "distance_traveled" in msg


def test_requires_bare_float_raises():
    with pytest.raises(DimensionError) as exc_info:
        distance_traveled(10, 5 * s)
    msg = str(exc_info.value)
    assert "bare" in msg.lower() or "no unit" in msg.lower()


def test_requires_second_param_wrong():
    with pytest.raises(DimensionError) as exc_info:
        distance_traveled(10 * m / s, 5 * m)
    msg = str(exc_info.value)
    assert "time" in msg


# ---------------------------------------------------------------------------
# @returns
# ---------------------------------------------------------------------------

@returns(Dim("m"))
def position(x):
    return x


def test_returns_correct():
    result = position(5 * m)
    assert result.magnitude == 5.0


def test_returns_wrong_dimension_raises():
    with pytest.raises(DimensionError) as exc_info:
        position(5 * kg)
    msg = str(exc_info.value)
    assert "position" in msg


# ---------------------------------------------------------------------------
# Stacked decorators
# ---------------------------------------------------------------------------

@requires(speed=Dim("m/s"), time=Dim("s"))
@returns(Dim("m"))
def calc_distance(speed, time):
    return speed * time


def test_stacked_correct():
    result = calc_distance(2 * m / s, 3 * s)
    assert math.isclose(result.magnitude, 6.0)


def test_stacked_wrong_input():
    with pytest.raises(DimensionError):
        calc_distance(2 * kg, 3 * s)


# ---------------------------------------------------------------------------
# Dim expression parsing
# ---------------------------------------------------------------------------

def test_dim_simple():
    d = Dim("m")
    from unitful.dimension import Dimension
    assert d.dimension == Dimension(L=1)


def test_dim_division():
    d = Dim("m/s")
    from unitful.dimension import Dimension
    assert d.dimension == Dimension(L=1, T=-1)


def test_dim_power():
    d = Dim("m/s^2")
    from unitful.dimension import Dimension
    assert d.dimension == Dimension(L=1, T=-2)


def test_dim_product():
    d = Dim("kg*m/s^2")
    from unitful.dimension import Dimension
    assert d.dimension == Dimension(M=1, L=1, T=-2)


def test_dim_unknown_raises():
    with pytest.raises(ValueError):
        Dim("zorgblatt")


# ---------------------------------------------------------------------------
# @requires with keyword-only call
# ---------------------------------------------------------------------------

@requires(mass=Dim("kg"))
def weigh(mass):
    return mass


def test_requires_keyword_arg():
    result = weigh(mass=70 * kg)
    assert result.magnitude == 70.0
