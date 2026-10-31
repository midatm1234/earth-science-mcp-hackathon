"""Science tests with hand-computed expected values. Replace with tests of your own functions."""

import math

import pytest

import science


def test_summary_hand_computed():
    out = science.summarize_values([1.0, None, 3.0, -9999.0, math.nan], "degC", fill_value=-9999.0)
    assert out["n_total"] == 5
    assert out["n_valid"] == 2
    assert out["n_missing"] == 3
    assert out["mean"] == pytest.approx(2.0)
    assert (out["min"], out["max"]) == (1.0, 3.0)


def test_all_missing_is_an_error():
    with pytest.raises(science.DataError, match="missing"):
        science.summarize_values([None, -9999.0], "degC", fill_value=-9999.0)


def test_units_required():
    with pytest.raises(science.DataError, match="units"):
        science.summarize_values([1.0], " ")
