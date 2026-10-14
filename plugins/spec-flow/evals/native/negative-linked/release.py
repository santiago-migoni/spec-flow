import re


_RELEASE_PATTERN = re.compile(r"v?((?!0\d)\d+)\.((?!0\d)\d+)\.((?!0\d)\d+)")


def normalize_release(value):
    if not isinstance(value, str):
        raise TypeError("release version must be a string")

    match = _RELEASE_PATTERN.fullmatch(value)
    if match is None:
        raise ValueError("release version must have three numeric components")

    return value if value.startswith("v") else f"v{value}"
