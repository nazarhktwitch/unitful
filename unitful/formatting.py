"""Formatting helpers for Quantity.__format__"""

from __future__ import annotations

import re
from re import Match


def _split_spec(format_spec: str) -> tuple[str, str]:
    """Split '0.2f~P' into ('0.2f', 'P').  Returns ('', '') for empty spec"""
    match = re.match(r"^([^~]*)(?:~([A-Za-z]+))?$", format_spec)
    if not match:
        return format_spec, ""
    num_spec, mode = match.group(1) or "", match.group(2) or ""
    return num_spec, mode.upper()


def _format_number(value: float, num_spec: str) -> str:
    """Format a bare float with a numeric format spec"""
    if num_spec:
        return format(value, num_spec)
    return str(value)


# Unicode superscript digits/signs
_SUPERSCRIPTS = str.maketrans("0123456789+-", "\u2070\u00b9\u00b2\u00b3\u2074\u2075\u2076\u2077\u2078\u2079\u207a\u207b")


def _to_superscript(s: str) -> str:
    return s.translate(_SUPERSCRIPTS)


def _unit_to_unicode(unit_str: str) -> str:
    """Convert 'm/s^2' style unit string to Unicode superscript form"""
    # Replace ^ followed by digits/sign with superscript chars
    def replace_exp(m: Match[str]) -> str:
        return _to_superscript(m.group(1))

    result = re.sub(r"\^([-+]?\d+(?:/\d+)?)", replace_exp, unit_str)
    # Replace * with middle dot (Unicode U+00B7)
    result = result.replace("*", "\u00b7")
    return result


def _unit_to_latex(unit_str: str) -> str:
    """Convert unit string to LaTeX \\mathrm notation"""
    # Split numerator / denominator on '/'
    if "/" in unit_str:
        parts = unit_str.split("/", 1)
        num = _part_to_latex(parts[0])
        den = _part_to_latex(parts[1])
        return rf"\frac{{{num}}}{{{den}}}"
    return _part_to_latex(unit_str)


def _part_to_latex(s: str) -> str:
    tokens = s.split("*")
    result = []
    for tok in tokens:
        if "^" in tok:
            base, exp = tok.split("^", 1)
            result.append(rf"\mathrm{{{base}}}^{{{exp}}}")
        else:
            result.append(rf"\mathrm{{{tok}}}")
    return r"\," .join(result)


def _sci_to_unicode(value: float, num_spec: str) -> str:
    """Format value with possible scientific notation in Unicode style"""
    formatted = _format_number(value, num_spec)
    # Check for e-notation
    if "e" in formatted or "E" in formatted:
        mantissa, exp_part = re.split(r"[eE]", formatted, maxsplit=1)
        exp_int = int(exp_part)
        return f"{mantissa} \u00d7 10{_to_superscript(str(exp_int))}"
    return formatted


def format_plain(value: float, unit_str: str, num_spec: str) -> str:
    return f"{_format_number(value, num_spec)} {unit_str}"


def format_unicode(value: float, unit_str: str, num_spec: str) -> str:
    num_part = _sci_to_unicode(value, num_spec)
    unit_part = _unit_to_unicode(unit_str)
    return f"{num_part} {unit_part}"


def format_latex(value: float, unit_str: str, num_spec: str) -> str:
    formatted = _format_number(value, num_spec)
    if "e" in formatted or "E" in formatted:
        mantissa, exp_part = re.split(r"[eE]", formatted, maxsplit=1)
        exp_int = int(exp_part)
        num_part = rf"{mantissa} \times 10^{{{exp_int}}}"
    else:
        num_part = formatted
    unit_part = _unit_to_latex(unit_str)
    return rf"{num_part}\,{unit_part}"


def format_html(value: float, unit_str: str, num_spec: str) -> str:
    inner = format_unicode(value, unit_str, num_spec)
    return f"<span>{inner}</span>"


def apply_format(value: float, unit_str: str, format_spec: str) -> str:
    num_spec, mode = _split_spec(format_spec)
    if mode == "P":
        return format_unicode(value, unit_str, num_spec)
    if mode == "L":
        return format_latex(value, unit_str, num_spec)
    if mode == "H":
        return format_html(value, unit_str, num_spec)
    return format_plain(value, unit_str, num_spec)
