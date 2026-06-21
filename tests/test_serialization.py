"""Tests for to_json / from_json and pickle serialization"""

import copy
import json
import math
import pickle
import pytest

from unitful import (
    Quantity,
    DimensionError,
    to_json, from_json,
    m, s, kg,
)
from unitful.dimension import Dimension


# ---------------------------------------------------------------------------
# to_json
# ---------------------------------------------------------------------------

def test_to_json_keys():
    q = 100.0 * m
    d = to_json(q)
    assert "value" in d
    assert "unit" in d
    assert "dimensions" in d


def test_to_json_value():
    q = 42.5 * m
    d = to_json(q)
    assert d["value"] == 42.5


def test_to_json_unit():
    q = 100.0 * m / s
    d = to_json(q)
    # unit key holds symbol string
    assert isinstance(d["unit"], str)


def test_to_json_dimensions_length():
    q = 1.0 * m
    d = to_json(q)
    assert d["dimensions"].get("L") == 1


def test_to_json_dimensions_velocity():
    q = (1.0 * m) / (1.0 * s)
    d = to_json(q)
    assert d["dimensions"].get("L") == 1
    assert d["dimensions"].get("T") == -1


def test_to_json_is_serializable():
    q = 100.0 * m
    # Must be JSON-serializable without extra encoders
    json.dumps(to_json(q))


# ---------------------------------------------------------------------------
# from_json
# ---------------------------------------------------------------------------

def test_from_json_roundtrip_m():
    q = 42.5 * m
    restored = from_json(to_json(q))
    assert math.isclose(restored.magnitude, 42.5)
    assert restored.unit.symbol == "m"


def test_from_json_roundtrip_kg():
    q = 70.0 * kg
    restored = from_json(to_json(q))
    assert math.isclose(restored.magnitude, 70.0)


def test_from_json_dict_only_value_unit():
    restored = from_json({"value": 9.8, "unit": "m"})
    assert math.isclose(restored.magnitude, 9.8)


def test_from_json_unknown_unit_raises():
    with pytest.raises(ValueError, match="Unknown unit"):
        from_json({"value": 1.0, "unit": "zorgblatt"})


# ---------------------------------------------------------------------------
# Pickle
# ---------------------------------------------------------------------------

def test_pickle_roundtrip():
    q = 100.0 * m
    restored = pickle.loads(pickle.dumps(q))
    assert restored == q


def test_pickle_preserves_unit():
    q = 9.8 * m / s ** 2
    restored = pickle.loads(pickle.dumps(q))
    assert math.isclose(restored.magnitude, 9.8)
    assert restored.dimension == q.dimension


# ---------------------------------------------------------------------------
# copy
# ---------------------------------------------------------------------------

def test_copy_shallow():
    q = 42.5 * m
    c = copy.copy(q)
    assert c == q
    assert c is not q


def test_copy_deep():
    q = 42.5 * m
    c = copy.deepcopy(q)
    assert c == q
    assert c is not q
