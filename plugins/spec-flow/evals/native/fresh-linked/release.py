import re


_COMPONENT = r"(?:0|[1-9][0-9]*)"
_VERSION_RE = re.compile(rf"v?{_COMPONENT}\.{_COMPONENT}\.{_COMPONENT}")


def normalize_release(value):
    if not isinstance(value, str):
        raise TypeError("release version must be a string")
    if _VERSION_RE.fullmatch(value) is None:
        raise ValueError("release version must have three numeric components")
    return value if value.startswith("v") else f"v{value}"
