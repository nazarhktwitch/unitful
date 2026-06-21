# unitful

[![PyPI version](https://img.shields.io/pypi/v/unitful.svg?style=flat-square&color=blue)](https://pypi.org/project/unitful/)
[![Python](https://img.shields.io/pypi/pyversions/unitful.svg?style=flat-square)](https://pypi.org/project/unitful/)
[![CI](https://img.shields.io/github/actions/workflow/status/nazarhktwitch/unitful/publish.yml?style=flat-square&label=CI)](https://github.com/nazarhktwitch/unitful/actions)
[![Coverage](https://img.shields.io/codecov/c/github/nazarhktwitch/unitful?style=flat-square)](https://codecov.io/gh/nazarhktwitch/unitful)
[![License](https://img.shields.io/pypi/l/unitful.svg?style=flat-square)](LICENSE)
[![Downloads](https://img.shields.io/pypi/dm/unitful?style=flat-square&color=green)](https://pypi.org/project/unitful/)

Physical units as first-class Python values

Attach a unit to any number, arithmetic propagates units automatically
Dimension mismatches raise `DimensionError` at runtime instead of producing
silently wrong results

## Getting Started

```
pip install unitful
```

```python
from unitful import m, s, kg, km, h

distance = 100 * m
time     = 9.58 * s
speed    = distance / time        # Quantity(10.44, 'm/s')

speed.to(km / h)                  # Quantity(37.58, 'km/h')
speed.to(kg)                      # DimensionError: [Length/Time] != [Mass]
```

## Features

- Dimension checking: all arithmetic validates physical dimensions and raises
  `DimensionError` with a clear message on mismatch
- Unit conversion: `.to(unit)` converts between compatible units, including
  offset temperature scales (`degC`, `degF`, `K`)
- NumPy integration: `np.array([...]) * m` returns a `QuantityArray`; ufuncs
  and reduction functions (`np.mean`, `np.sum`, etc.) preserve units
- Decorators: `@requires` and `@returns` enforce dimensions on function
  arguments and return values
- Custom units and dimensions: `define_unit` and `new_dimension` extend the
  registry at runtime
- Serialization: `to_json` / `from_json` for plain-dict round-trips; pickle
  and `copy` work without extra setup
- Formatting: `f"{q:.2f~P}"` (Unicode), `f"{q:.2f~L}"` (LaTeX),
  `f"{q:.2f~H}"` (HTML)

## Requirements

Python 3.10 or later. NumPy is optional; install it with:

```
pip install "unitful[numpy]"
```

## License

[MIT](LICENSE)
