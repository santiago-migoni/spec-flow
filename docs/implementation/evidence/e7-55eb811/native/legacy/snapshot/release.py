import re


_RELEASE_PATTERN = re.compile(r"v?(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)")


def normalize_release(value):
    if not isinstance(value, str):
        raise TypeError("release must be a string")
    if _RELEASE_PATTERN.fullmatch(value) is None:
        raise ValueError("release must be a bare or v-prefixed numeric triple")
    return value if value.startswith("v") else f"v{value}"
