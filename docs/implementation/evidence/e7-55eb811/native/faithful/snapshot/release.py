import re


_RELEASE_PATTERN = re.compile(r"v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", re.ASCII)


def normalize_release(value):
    if not isinstance(value, str):
        raise TypeError("release must be a string")

    match = _RELEASE_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError("release must be a strict numeric triple")

    return "v" + ".".join(match.groups())
