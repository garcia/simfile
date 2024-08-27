from decimal import Decimal
import re


FLOAT_EXPRESSION = re.compile(r"[+-]?(\d+([.]\d*)?([eE][+-]?\d+)?|[.]\d+([eE][+-]?\d+)?)")


def extract_float_str(s: str) -> str:
    match_result = FLOAT_EXPRESSION.match(s)
    if match_result is None:
        return '0'
    else:
        return match_result[0]

def enforce_float_str(s: str, strict: bool, error_message: str) -> str:
    float_str = extract_float_str(s)
    if strict and float_str != s:
        raise ValueError('%s: %r', error_message, s)
    return float_str