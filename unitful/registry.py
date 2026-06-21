"""A unit registry that stores and looks up units by name/symbol"""

from __future__ import annotations

from dataclasses import dataclass
from typing import TYPE_CHECKING

from .dimension import Dimension

if TYPE_CHECKING:
    from .quantity import Quantity

# SI prefix table: symbol -> scale factor
_SI_PREFIXES: dict[str, float] = {
    "Y": 1e24,
    "Z": 1e21,
    "E": 1e18,
    "P": 1e15,
    "T": 1e12,
    "G": 1e9,
    "M": 1e6,
    "k": 1e3,
    "h": 1e2,
    "da": 1e1,
    "d": 1e-1,
    "c": 1e-2,
    "m": 1e-3,
    "u": 1e-6,   # ASCII fallback for μ
    "μ": 1e-6,
    "n": 1e-9,
    "p": 1e-12,
    "f": 1e-15,
    "a": 1e-18,
    "z": 1e-21,
    "y": 1e-24,
}


@dataclass(frozen=True)
class Unit:
    """A physical unit defined by a scale factor relative to SI base units

    `scale` converts this unit to the SI base combination
    `offset` is non-zero only for temperature units (degC, degF)
    """

    name: str
    symbol: str
    dimension: Dimension
    scale: float          # multiplicative factor to SI
    offset: float = 0.0  # additive offset (used for degC, degF -> K)

    @property
    def is_offset(self) -> bool:
        return self.offset != 0.0


class UnitRegistry:
    """Singleton registry mapping unit names/symbols to Unit objects"""

    _instance: UnitRegistry | None = None
    _by_name: dict[str, Unit]
    _by_symbol: dict[str, Unit]

    def __new__(cls) -> UnitRegistry:
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._by_name = {}
            cls._instance._by_symbol = {}
        return cls._instance

    def register(
        self,
        name: str,
        symbol: str,
        dimension: Dimension,
        scale: float,
        offset: float = 0.0,
    ) -> Unit:
        """Register a unit and return it"""
        unit = Unit(name=name, symbol=symbol, dimension=dimension, scale=scale, offset=offset)
        self._by_name[name] = unit
        self._by_symbol[symbol] = unit
        return unit

    def get(self, name: str) -> Unit:
        """Look up a unit by name or symbol; try SI prefix expansion on miss"""
        if name in self._by_name:
            return self._by_name[name]
        if name in self._by_symbol:
            return self._by_symbol[name]
        return self._parse_prefixed(name)

    def _parse_prefixed(self, name: str) -> Unit:
        # Try two-character prefix first (e.g. 'da'), then one-character
        for prefix_len in (2, 1):
            prefix = name[:prefix_len]
            rest = name[prefix_len:]
            if prefix in _SI_PREFIXES and rest:
                # Try to find the base unit by remainder
                try:
                    base = self.get(rest)
                except KeyError:
                    continue
                factor = _SI_PREFIXES[prefix]
                new_scale = base.scale * factor
                new_name = f"{prefix}{base.name}"
                new_symbol = f"{prefix}{base.symbol}"
                return Unit(
                    name=new_name,
                    symbol=new_symbol,
                    dimension=base.dimension,
                    scale=new_scale,
                )
        raise KeyError(f"Unknown unit: {name!r}")

    def define_unit(self, name: str, quantity: Quantity, symbol: str = "") -> Unit:
        """Register a new unit from a Quantity (its value is the scale to SI)"""
        sym = symbol or name
        unit = Unit(
            name=name,
            symbol=sym,
            dimension=quantity.unit.dimension,
            scale=quantity._to_si_value(),
        )
        self._by_name[name] = unit
        self._by_symbol[sym] = unit
        return unit

    def new_dimension(self, name: str, symbol: str = "") -> Dimension:
        """Create and register a new base dimension not in the SI set"""
        dim = Dimension.custom(name)
        # Register a base unit with scale=1 for this dimension
        sym = symbol or name
        unit = Unit(name=name, symbol=sym, dimension=dim, scale=1.0)
        self._by_name[name] = unit
        self._by_symbol[sym] = unit
        return dim

    def all_units(self) -> dict[str, Unit]:
        return dict(self._by_name)


# Module-level singleton
registry = UnitRegistry()
