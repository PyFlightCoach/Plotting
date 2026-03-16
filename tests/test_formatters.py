import numpy as np
from plotting.formatters import format_npi



def test_format_npi():
    assert format_npi(0) == "0"
    assert format_npi(-0) == "0"
    assert format_npi(np.pi / 2) == "π/2"
    assert format_npi(np.pi) == "π"
    assert format_npi(-np.pi) == "-π"
    assert format_npi(2 * np.pi) == "2π"
    assert format_npi(-2 * np.pi) == "-2π"
    assert format_npi(3 * np.pi / 2) == "3π/2"


def test_format_npi_iterable_inputs():
    assert format_npi([0, np.pi / 2, -np.pi]) == ["0", "π/2", "-π"]
    assert format_npi((2 * np.pi, -2 * np.pi)) == ["2π", "-2π"]
    assert format_npi(np.array([np.pi, 3 * np.pi / 2])) == ["π", "3π/2"]


def test_format_npi_custom_constant_scalar():
    assert format_npi(np.e / 2, pival="e", cval=np.e) == "e/2"
    assert format_npi(-2 * np.e, pival="e", cval=np.e) == "-2e"
    assert format_npi(2 * np.pi, pival="τ", cval=2 * np.pi) == "τ"


def test_format_npi_custom_constant_iterable():
    values = np.array([np.e, 3 * np.e / 2, -np.e / 2])
    assert format_npi(values, pival="e", cval=np.e) == ["e", "3e/2", "-e/2"]


def test_format_npi_custom_constant_requires_non_zero_value():
    try:
        format_npi(1.0, pival="k", cval=0.0)
    except ValueError as exc:
        assert str(exc) == "cval must be non-zero"
    else:
        raise AssertionError("Expected ValueError for zero cval")