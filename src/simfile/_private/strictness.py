from decimal import Decimal
import re


FLOAT_EXPRESSION = re.compile(
    r"[+-]?(\d+([.]\d*)?([eE][+-]?\d+)?|[.]\d+([eE][+-]?\d+)?)"
)
"""
Expression should match the behavior of `std::stof` used by StepMania:
https://en.cppreference.com/w/cpp/string/basic_string/stof
"""


def extract_float_str(s: str) -> str:
    """
    Extract a floating-point number from the start of a string,
    or "0" if none can be found
    """
    match_result = FLOAT_EXPRESSION.match(s)
    if match_result is None:
        return "0"
    else:
        return match_result[0]


def enforce_float_str(s: str, strict: bool, error_message: str) -> str:
    """
    Extract a floating-point number from the start of a string;
    if `strict`, raises ValueError unless the whole input string was matched
    """
    float_str = extract_float_str(s)
    if strict and float_str != s:
        raise ValueError("%s: %r", error_message, s)
    return float_str
