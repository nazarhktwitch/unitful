import pytest
from decimal import Decimal
from fractions import Fraction
import math

from unitful import Quantity, m, s, km, h, kg
from unitful.constants import c, G, hbar

def test_constants():
    assert c.magnitude == 299792458
    assert c.unit.symbol == "m/s"
    assert G.magnitude > 0
    assert hbar.magnitude > 0

def test_exact_arithmetic():
    q_dec = Decimal("10.5") * m
    assert q_dec.magnitude == Decimal("10.5")
    
    q_frac = Fraction(1, 3) * m
    assert q_frac.magnitude == Fraction(1, 3)
    
    # Check addition preserves Decimal types
    res = q_dec + Decimal("2.5") * m
    assert res.magnitude == Decimal("13.0")
    
    # Check equality works across float and Decimal
    assert q_dec == 10.5 * m

def test_from_string():
    q = Quantity.from_string("100 km/h")
    assert q.magnitude == 100.0
    assert q.unit.symbol == "km/h"
    
    q2 = Quantity.from_string("-9.81 m/s^2")
    assert q2.magnitude == -9.81
    assert q2.unit.symbol == "m/s^2"
    
    q3 = Quantity.from_string("1.5e3 kg")
    assert q3.magnitude == 1500.0

def test_pandas_accessor():
    pytest.importorskip("pandas")
    import pandas as pd
    from unitful import setup_pandas
    setup_pandas()
    
    s_raw = pd.Series([10.0, 20.0, 30.0])
    s_unit = s_raw.unitful.attach(m)
    assert isinstance(s_unit.iloc[0], Quantity)
    assert s_unit.iloc[0].unit == m
    
    s_conv = s_unit.unitful.to(km)
    assert math.isclose(s_conv.iloc[0], 0.01)

def test_matplotlib_support():
    pytest.importorskip("matplotlib")
    import matplotlib.units as munits
    from unitful import setup_matplotlib
    setup_matplotlib()
    
    assert Quantity in munits.registry
