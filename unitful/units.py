"""All built-in units registered at import time

Each named constant is a Quantity with value 1.0, so that arithmetic like
`100 * m` or `km / h` works naturally
"""

from __future__ import annotations

import math

from .dimension import Dimension
from .quantity import Quantity
from .registry import Unit, registry


def _q(name: str, symbol: str, dim: Dimension, scale: float, offset: float = 0.0) -> Quantity:
    """Register and return a unit as a Quantity(1.0, unit)"""
    unit = registry.register(name, symbol, dim, scale, offset)
    return Quantity(1.0, unit)


# --- Base SI dimensions ---
_L = Dimension(L=1)
_M = Dimension(M=1)
_T = Dimension(T=1)
_I = Dimension(I=1)
_Theta = Dimension(Theta=1)
_N_dim = Dimension(N=1)
_J = Dimension(J=1)


# Length
m   = _q("m",    "m",    _L, 1.0)
km  = _q("km",   "km",   _L, 1e3)
cm  = _q("cm",   "cm",   _L, 1e-2)
mm  = _q("mm",   "mm",   _L, 1e-3)
um  = _q("um",   "μm",   _L, 1e-6)   # ASCII alias
μm  = _q("μm",   "μm",   _L, 1e-6)
nm  = _q("nm",   "nm",   _L, 1e-9)

inch = _q("inch", "in",  _L, 0.0254)
ft   = _q("ft",   "ft",  _L, 0.3048)
yd   = _q("yd",   "yd",  _L, 0.9144)
mile = _q("mile", "mi",  _L, 1609.344)
nmi  = _q("nmi",  "nmi", _L, 1852.0)
ly   = _q("ly",   "ly",  _L, 9.4607304725808e15)


# Mass
kg   = _q("kg",    "kg",  _M, 1.0)
g    = _q("g",     "g",   _M, 1e-3)
mg   = _q("mg",    "mg",  _M, 1e-6)
ug   = _q("ug",    "μg",  _M, 1e-9)   # ASCII alias
μg   = _q("μg",    "μg",  _M, 1e-9)
t    = _q("t",     "t",   _M, 1e3)    # metric ton
lb   = _q("lb",    "lb",  _M, 0.45359237)
oz   = _q("oz",    "oz",  _M, 0.028349523125)
stone = _q("stone", "st", _M, 6.35029318)


# Time
s    = _q("s",    "s",    _T, 1.0)
ms   = _q("ms",   "ms",   _T, 1e-3)
us   = _q("us",   "μs",   _T, 1e-6)   # ASCII alias
μs   = _q("μs",   "μs",   _T, 1e-6)
ns   = _q("ns",   "ns",   _T, 1e-9)

# 'min' is a Python built-in, but as a module variable this is fine
min  = _q("min",  "min",  _T, 60.0)
h    = _q("h",    "h",    _T, 3600.0)
day  = _q("day",  "day",  _T, 86400.0)
week = _q("week", "week", _T, 604800.0)
year = _q("year", "yr",   _T, 31557600.0)   # Julian year


# Temperature
# All temperatures convert to Kelvin as SI base
# scale: multiply value by this, then add offset, to get Kelvin
K    = _q("K",    "K",    _Theta, 1.0,    0.0)
degC = _q("degC", "degC", _Theta, 1.0,    273.15)
degF = _q("degF", "degF", _Theta, 5/9,    273.15 - 32 * 5/9)


# Current
A    = _q("A",    "A",    _I, 1.0)
mA   = _q("mA",   "mA",   _I, 1e-3)

# Amount of substance
mol  = _q("mol",  "mol",  _N_dim, 1.0)

# Luminous intensity
cd   = _q("cd",   "cd",   _J, 1.0)


# Force
_Force = Dimension(M=1, L=1, T=-2)
N_unit = _q("N",   "N",   _Force, 1.0)
kN     = _q("kN",  "kN",  _Force, 1e3)
MN     = _q("MN",  "MN",  _Force, 1e6)
lbf    = _q("lbf", "lbf", _Force, 4.4482216152605)


# Energy
_Energy = Dimension(M=1, L=2, T=-2)
J    = _q("J",    "J",    _Energy, 1.0)
kJ   = _q("kJ",   "kJ",   _Energy, 1e3)
MJ   = _q("MJ",   "MJ",   _Energy, 1e6)
cal  = _q("cal",  "cal",  _Energy, 4.184)
kcal = _q("kcal", "kcal", _Energy, 4184.0)
eV   = _q("eV",   "eV",   _Energy, 1.602176634e-19)
kWh  = _q("kWh",  "kWh",  _Energy, 3.6e6)


# Power
_Power = Dimension(M=1, L=2, T=-3)
W    = _q("W",    "W",    _Power, 1.0)
kW   = _q("kW",   "kW",   _Power, 1e3)
MW   = _q("MW",   "MW",   _Power, 1e6)
hp   = _q("hp",   "hp",   _Power, 745.69987158227)


# Pressure
_Pressure = Dimension(M=1, L=-1, T=-2)
Pa   = _q("Pa",   "Pa",   _Pressure, 1.0)
kPa  = _q("kPa",  "kPa",  _Pressure, 1e3)
MPa  = _q("MPa",  "MPa",  _Pressure, 1e6)
bar  = _q("bar",  "bar",  _Pressure, 1e5)
atm  = _q("atm",  "atm",  _Pressure, 101325.0)
psi  = _q("psi",  "psi",  _Pressure, 6894.757293168)


# Speed
_Speed = Dimension(L=1, T=-1)
# 'm/s' and 'km/h' are computed dynamically from base units;
# we register them as names for serialization lookup
_ms_unit   = registry.register("m/s",   "m/s",   _Speed, 1.0)
_kmh_unit  = registry.register("km/h",  "km/h",  _Speed, 1/3.6)
mph   = _q("mph",   "mph",   _Speed, 0.44704)
knot  = _q("knot",  "kn",    _Speed, 0.514444)
mach  = _q("mach",  "mach",  _Speed, 340.29)


# Data
_Data = Dimension.custom("data")
registry._by_name["data"] = Unit("data", "bit", _Data, 1.0)
registry._by_symbol["bit"] = registry._by_name["data"]

bit  = _q("bit",  "bit",  _Data, 1.0)
B    = _q("B",    "B",    _Data, 8.0)
KB   = _q("KB",   "KB",   _Data, 8e3)
MB   = _q("MB",   "MB",   _Data, 8e6)
GB   = _q("GB",   "GB",   _Data, 8e9)
TB   = _q("TB",   "TB",   _Data, 8e12)
KiB  = _q("KiB",  "KiB",  _Data, 8 * 1024)
MiB  = _q("MiB",  "MiB",  _Data, 8 * 1024**2)
GiB  = _q("GiB",  "GiB",  _Data, 8 * 1024**3)


# Angle
_Angle = Dimension.custom("angle")
registry._by_name["angle"] = Unit("angle", "rad", _Angle, 1.0)
registry._by_symbol["rad_base"] = registry._by_name["angle"]

rad    = _q("rad",    "rad",    _Angle, 1.0)
deg    = _q("deg",    "deg",    _Angle, math.pi / 180)
arcmin = _q("arcmin", "arcmin", _Angle, math.pi / 10800)
arcsec = _q("arcsec", "arcsec", _Angle, math.pi / 648000)
