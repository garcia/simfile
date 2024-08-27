from textwrap import dedent


def dedent_and_trim(string: str) -> str:
    return dedent(string.lstrip("\r\n").rstrip(" "))
