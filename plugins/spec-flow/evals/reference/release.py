"""Normalize strict three-component release versions."""

import re


_RELEASE_PATTERN = re.compile(
    r"v?(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)\.(?:0|[1-9][0-9]*)"
)


def normalize_release(value):
    """Return a canonical ``vMAJOR.MINOR.PATCH`` release string.

    Raise TypeError for nonstrings and ValueError for malformed versions.
    """
    if not isinstance(value, str):
        raise TypeError("release version must be a string")
    if _RELEASE_PATTERN.fullmatch(value) is None:
        raise ValueError("release version must be MAJOR.MINOR.PATCH or vMAJOR.MINOR.PATCH")
    return value if value.startswith("v") else "v" + value
