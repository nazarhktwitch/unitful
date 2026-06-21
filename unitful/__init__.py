"""Public API"""

from . import numpy_support  # noqa: F401
from . import constants  # noqa: F401
from .matplotlib_support import setup_matplotlib  # noqa: F401
from .pandas_support import setup_pandas  # noqa: F401
from .decorators import Dim, requires, returns
from .dimension import Dimension, dimensionless
from .exceptions import DimensionError
from .numpy_support import QuantityArray
from .quantity import Quantity
from .registry import Unit, registry
from .serialization import from_json, to_json

# All built-in unit constants are imported from units.py
from .units import (
    GB,
    KB,
    MB,
    MJ,
    MN,
    MW,
    TB,
    B,
    GiB,
    # Energy
    J,
    # Temperature
    K,
    KiB,
    MiB,
    MPa,
    # Force
    N_unit,
    # Pressure
    Pa,
    # Power
    W,
    arcmin,
    arcsec,
    atm,
    bar,
    # Data
    bit,
    cal,
    cm,
    day,
    deg,
    degC,
    degF,
    eV,
    ft,
    g,
    h,
    hp,
    inch,
    kcal,
    # Mass
    kg,
    kJ,
    km,
    kN,
    knot,
    kPa,
    kW,
    kWh,
    lb,
    lbf,
    ly,
    # Length
    m,
    mach,
    mg,
    mile,
    min,
    mm,
    # Speed
    mph,
    ms,
    nm,
    nmi,
    ns,
    oz,
    psi,
    # Angle
    rad,
    # Time
    s,
    stone,
    t,
    ug,
    um,
    us,
    week,
    yd,
    year,
    μg,
    μm,
    μs,
)

# Newton exported as N (N_unit avoids clash with the Amount dimension symbol)
N = N_unit


def new_dimension(name: str, symbol: str = "") -> Dimension:
    """Register and return a new base dimension

    Example::

        px = new_dimension("pixel", symbol="px")
    """
    return registry.new_dimension(name, symbol)


def define_unit(name: str, quantity: Quantity, symbol: str = "") -> Quantity:
    """Register a new unit derived from an existing Quantity

    Example::

        define_unit("furlong", 201.168 * m)
        define_unit("fortnight", 14 * day)
    """
    unit = registry.define_unit(name, quantity, symbol)
    return Quantity(1.0, unit)


__all__ = [
    # Core types
    "Quantity",
    "QuantityArray",
    "Dimension",
    "dimensionless",
    "DimensionError",
    "Unit",
    # Registry helpers
    "new_dimension",
    "define_unit",
    # Decorators
    "requires",
    "returns",
    "Dim",
    # Serialization
    "to_json",
    "from_json",
    # Length
    "m", "km", "cm", "mm", "μm", "um", "nm",
    "inch", "ft", "yd", "mile", "nmi", "ly",
    # Mass
    "kg", "g", "mg", "μg", "ug", "t", "lb", "oz", "stone",
    # Time
    "s", "ms", "μs", "us", "ns", "min", "h", "day", "week", "year",
    # Temperature
    "K", "degC", "degF",
    # Force
    "N", "kN", "MN", "lbf",
    # Energy
    "J", "kJ", "MJ", "cal", "kcal", "eV", "kWh",
    # Power
    "W", "kW", "MW", "hp",
    # Pressure
    "Pa", "kPa", "MPa", "bar", "atm", "psi",
    # Speed
    "mph", "knot", "mach",
    # Data
    "bit", "B", "KB", "MB", "GB", "TB", "KiB", "MiB", "GiB",
    # Angle
    "rad", "deg", "arcmin", "arcsec",
]
