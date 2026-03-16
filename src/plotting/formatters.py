import numpy as np
from fractions import Fraction
from typing import Iterable, overload


@overload
def format_npi(
    x: float, pival: str = "π", cval: float = np.pi, tol: float = 1e-5
) -> str: ...


@overload
def format_npi(
    x: Iterable[float], pival: str = "π", cval: float = np.pi, tol: float = 1e-5
) -> list[str]: ...


def format_npi(
    x: float | Iterable[float], pival: str = "π", cval: float = np.pi, tol: float = 1e-5
) -> str | list[str]:
    if hasattr(x, "__iter__"):
        return [format_npi(xi, pival, cval, tol) for xi in x]
    if abs(x) < tol:
        return "0"
    if abs(cval) < tol:
        raise ValueError("cval must be non-zero")
    frac = Fraction(abs(x) / cval).limit_denominator()
    nom = frac.numerator if frac.numerator != 1 else ""
    denom = f"/{frac.denominator}" if frac.denominator != 1 else ""
    sign = "-" if x < 0 else ""
    return f"{sign}{nom}{pival}{denom}"


def npi_axis_props(
    start: float,
    stop: float,
    step: float,
    range: list[float] | None = None,
    pival: str = "π",
    cval: float = np.pi,
):
    if range is None:
        range = [start, stop]
    n = int(np.ceil((stop - start) / step)) + 1
    ticks = np.linspace(start, stop, n)
    ticktext = format_npi(ticks, pival, cval)
    return dict(
        range=range,
        tickmode="array",
        tickvals=ticks,
        ticktext=ticktext,
    )
