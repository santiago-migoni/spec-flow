import re


_RELEASE_PATTERN = re.compile(r"v?(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)\.(0|[1-9][0-9]*)", re.ASCII)


def normalize_release(value):
    if not isinstance(value, str):
        raise TypeError("release version must be a string")

    match = _RELEASE_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError("release version must be X.Y.Z or vX.Y.Z")

    return f"v{match.group(1)}.{match.group(2)}.{match.group(3)}"
