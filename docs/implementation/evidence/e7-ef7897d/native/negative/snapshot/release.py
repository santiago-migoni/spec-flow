import re


_RELEASE_PATTERN = re.compile(r"v?([0-9]+)\.([0-9]+)\.([0-9]+)")


def normalize_release(value):
    if not isinstance(value, str):
        raise TypeError("release must be a string")

    match = _RELEASE_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError("release must be an ASCII numeric triple")

    major, minor, patch = match.groups()
    if any(len(component) > 1 and component.startswith("0") for component in (major, minor)):
        raise ValueError("release components must not have leading zeros")

    return f"v{major}.{minor}.{patch}"
