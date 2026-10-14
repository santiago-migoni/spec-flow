import re


_RELEASE_PATTERN = re.compile(r"v?(\d+)\.(\d+)\.(\d+)\Z")


def normalize_release(value):
    if not isinstance(value, str):
        raise TypeError("release must be a string")
    match = _RELEASE_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError("release must have three numeric components")
    return "v" + ".".join(match.groups())
