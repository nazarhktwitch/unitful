"""Tests for Dimension class"""

import pytest
from fractions import Fraction

from unitful.dimension import (
    Dimension,
    dimensionless,
    Length,
    Mass,
    Time,
    Current,
    Temperature,
    Amount,
    Luminosity,
)


def test_equality():
    assert Dimension(L=1) == Dimension(L=1)
    assert Dimension(L=1) != Dimension(M=1)
    assert Dimension(L=1, T=-1) == Dimension(L=1, T=-1)


def test_hash_equal_dimensions():
    a = Dimension(L=1, T=-1)
    b = Dimension(L=1, T=-1)
    assert hash(a) == hash(b)
    assert a in {b}


def test_multiply():
    result = Dimension(M=1) * Dimension(L=1, T=-2)
    assert result == Dimension(M=1, L=1, T=-2)


def test_divide():
    result = Dimension(L=1) / Dimension(T=1)
    assert result == Dimension(L=1, T=-1)


def test_power_integer():
    result = Dimension(L=1) ** 2
    assert result == Dimension(L=2)


def test_power_fraction():
    result = Dimension(L=2) ** Fraction(1, 2)
    assert result == Dimension(L=1)


def test_power_negative():
    result = Dimension(T=1) ** -1
    assert result == Dimension(T=-1)


def test_dimensionless():
    assert dimensionless.is_dimensionless()
    assert Dimension() == dimensionless


def test_is_dimensionless_false():
    assert not Length.is_dimensionless()


def test_multiply_cancel():
    result = Dimension(L=1) * Dimension(L=-1)
    assert result.is_dimensionless()


def test_singletons():
    assert Length == Dimension(L=1)
    assert Mass == Dimension(M=1)
    assert Time == Dimension(T=1)
    assert Current == Dimension(I=1)
    assert Temperature == Dimension(Theta=1)
    assert Amount == Dimension(N=1)
    assert Luminosity == Dimension(J=1)


def test_str_dimensionless():
    assert str(dimensionless) == "dimensionless"


def test_str_single():
    assert str(Dimension(L=1)) == "L"


def test_str_compound():
    s = str(Dimension(L=1, T=-1))
    assert "L" in s
    assert "T^-1" in s


def test_label_length():
    assert "Length" in Length.label()


def test_label_velocity():
    vel = Dimension(L=1, T=-1)
    label = vel.label()
    assert "Length" in label
    assert "Time" in label


def test_label_dimensionless():
    assert dimensionless.label() == "dimensionless"


def test_custom_dimension():
    dim = Dimension.custom("pixel")
    assert dim["pixel"] == Fraction(1)
    assert dim["L"] == Fraction(0)


def test_from_dict_internal():
    d = {k: Fraction(0) for k in ("L", "M", "T", "I", "Theta", "N", "J")}
    d["L"] = Fraction(1)
    dim = Dimension._from_dict(d)
    assert dim == Length


def test_getitem_default():
    assert Dimension(L=1)["M"] == Fraction(0)


def test_repr():
    r = repr(Dimension(L=1))
    assert "Dimension" in r
