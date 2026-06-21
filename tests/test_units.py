"""Tests for built-in units and registry"""

import math
import pytest

from unitful import (
    m, km, cm, mm, nm,
    inch, ft, yd, mile, nmi,
    kg, g, mg, lb, oz, stone, t,
    s, ms, min, h, day, week, year,
    K, degC, degF,
    N, kN, lbf,
    J, kJ, cal, kcal, eV, kWh,
    W, kW, hp,
    Pa, kPa, bar, atm, psi,
    mph, knot, mach,
    bit, B, KB, MB, GB,
    rad, deg, arcmin, arcsec,
    DimensionError,
    define_unit, new_dimension,
    Quantity,
)


# ── Length ───────────────────────────────────────────────────────────────────

def test_km_to_m():
    assert math.isclose((1 * km).to(m).magnitude, 1000.0)


def test_cm_to_m():
    assert math.isclose((100 * cm).to(m).magnitude, 1.0)


def test_mm_to_m():
    assert math.isclose((1000 * mm).to(m).magnitude, 1.0)


def test_inch_to_m():
    assert math.isclose((1 * inch).to(m).magnitude, 0.0254, rel_tol=1e-6)


def test_ft_to_m():
    assert math.isclose((1 * ft).to(m).magnitude, 0.3048, rel_tol=1e-6)


def test_mile_to_m():
    assert math.isclose((1 * mile).to(m).magnitude, 1609.344, rel_tol=1e-6)


def test_nmi_to_m():
    assert math.isclose((1 * nmi).to(m).magnitude, 1852.0, rel_tol=1e-6)


# Mass

def test_g_to_kg():
    assert math.isclose((1000 * g).to(kg).magnitude, 1.0)


def test_mg_to_g():
    assert math.isclose((1000 * mg).to(g).magnitude, 1.0)


def test_lb_to_kg():
    assert math.isclose((1 * lb).to(kg).magnitude, 0.45359237, rel_tol=1e-6)


def test_oz_to_g():
    assert math.isclose((1 * oz).to(g).magnitude, 28.349523, rel_tol=1e-4)


def test_stone_to_kg():
    assert math.isclose((1 * stone).to(kg).magnitude, 6.35029318, rel_tol=1e-6)


def test_t_to_kg():
    assert math.isclose((1 * t).to(kg).magnitude, 1000.0)


# Time

def test_min_to_s():
    assert math.isclose((1 * min).to(s).magnitude, 60.0)


def test_h_to_s():
    assert math.isclose((1 * h).to(s).magnitude, 3600.0)


def test_day_to_h():
    assert math.isclose((1 * day).to(h).magnitude, 24.0)


def test_week_to_day():
    assert math.isclose((1 * week).to(day).magnitude, 7.0)


def test_ms_to_s():
    assert math.isclose((1000 * ms).to(s).magnitude, 1.0)


# Temperature

def test_0_degc_to_k():
    assert math.isclose((0 * degC).to(K).magnitude, 273.15, rel_tol=1e-6)


def test_100_degc_to_k():
    assert math.isclose((100 * degC).to(K).magnitude, 373.15, rel_tol=1e-6)


def test_32_degf_to_k():
    assert math.isclose((32 * degF).to(K).magnitude, 273.15, rel_tol=1e-6)


def test_212_degf_to_degc():
    assert math.isclose((212 * degF).to(degC).magnitude, 100.0, rel_tol=1e-5)


def test_k_to_degc():
    assert math.isclose((273.15 * K).to(degC).magnitude, 0.0, abs_tol=1e-9)


# Force

def test_kn_to_n():
    assert math.isclose((1 * kN).to(N).magnitude, 1000.0)


def test_lbf_to_n():
    assert math.isclose((1 * lbf).to(N).magnitude, 4.44822, rel_tol=1e-4)


# Energy

def test_kj_to_j():
    assert math.isclose((1 * kJ).to(J).magnitude, 1000.0)


def test_kcal_to_cal():
    assert math.isclose((1 * kcal).to(cal).magnitude, 1000.0)


def test_kwh_to_j():
    assert math.isclose((1 * kWh).to(J).magnitude, 3.6e6, rel_tol=1e-9)


def test_ev_to_j():
    assert math.isclose((1 * eV).to(J).magnitude, 1.602176634e-19, rel_tol=1e-9)


# Power

def test_kw_to_w():
    assert math.isclose((1 * kW).to(W).magnitude, 1000.0)


def test_hp_to_w():
    assert math.isclose((1 * hp).to(W).magnitude, 745.69987, rel_tol=1e-5)


# Pressure

def test_atm_to_pa():
    assert math.isclose((1 * atm).to(Pa).magnitude, 101325.0)


def test_bar_to_pa():
    assert math.isclose((1 * bar).to(Pa).magnitude, 1e5)


def test_kpa_to_pa():
    assert math.isclose((1 * kPa).to(Pa).magnitude, 1000.0)


def test_psi_to_pa():
    assert math.isclose((1 * psi).to(Pa).magnitude, 6894.757, rel_tol=1e-4)


# Speed

def test_mph_to_ms():
    assert math.isclose((1 * mph).to(m / s).magnitude, 0.44704, rel_tol=1e-6)


def test_knot_to_ms():
    assert math.isclose((1 * knot).to(m / s).magnitude, 0.514444, rel_tol=1e-4)


# Data

def test_b_to_bit():
    assert math.isclose((1 * B).to(bit).magnitude, 8.0)


def test_kb_to_b():
    assert math.isclose((1 * KB).to(B).magnitude, 1000.0)


def test_gb_to_mb():
    assert math.isclose((1 * GB).to(MB).magnitude, 1000.0)


# Angle

def test_deg_to_rad():
    assert math.isclose((180 * deg).to(rad).magnitude, math.pi, rel_tol=1e-9)


def test_arcmin_to_deg():
    assert math.isclose((60 * arcmin).to(deg).magnitude, 1.0, rel_tol=1e-9)


def test_arcsec_to_arcmin():
    assert math.isclose((60 * arcsec).to(arcmin).magnitude, 1.0, rel_tol=1e-9)


# Custom units

def test_define_unit():
    furlong = define_unit("furlong", 201.168 * m)
    assert math.isclose((1 * furlong).to(m).magnitude, 201.168, rel_tol=1e-6)


def test_define_unit_time():
    fortnight = define_unit("fortnight", 14 * day)
    assert math.isclose((1 * fortnight).to(day).magnitude, 14.0, rel_tol=1e-9)


def test_new_dimension():
    px = new_dimension("pixel2", symbol="px2")
    from unitful.registry import registry
    unit = registry.get("pixel2")
    q = 1920 * Quantity(1.0, unit)
    assert q.magnitude == 1920.0


def test_dimension_mismatch_custom():
    px = new_dimension("pixel3", symbol="px3")
    from unitful.registry import registry
    px_unit = registry.get("pixel3")
    px_qty = Quantity(1.0, px_unit)
    with pytest.raises(DimensionError):
        (1 * m).to(px_qty)
