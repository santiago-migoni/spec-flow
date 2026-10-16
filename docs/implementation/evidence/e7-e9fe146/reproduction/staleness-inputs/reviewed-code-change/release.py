import re


_RELEASE_PATTERN = re.compile(r"v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", re.ASCII)


def normalize_release(value):
    if not isinstance(value, str):
        raise TypeError("release must be a string")

    match = _RELEASE_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError("release must be an ASCII numeric triple")

    return f"v{match.group(1)}.{match.group(2)}.{match.group(3)}"

# E7 deliberately changed after reviewed audit
