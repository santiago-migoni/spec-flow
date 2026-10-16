"""Validated role profiles; immutable run snapshots preserve historical choices."""
import copy
import re

LEGACY_PROFILES = {
    'orchestrator': {'id': 'gpt-6-sol', 'effort': 'high'},
    'implementer': {'id': 'gpt-6-luna', 'effort': 'high'},
    'reviewer': {'id': 'gpt-6-sol', 'effort': 'high'},
}
DEFAULT_PROFILES = {
    'orchestrator': {'id': 'gpt-6.1-sol', 'effort': 'low'},
    'implementer': {'id': 'gpt-6-luna', 'effort': 'high'},
    'reviewer': {'id': 'gpt-6.1-sol', 'effort': 'medium'},
}
EFFORTS = {'none', 'minimal', 'low', 'medium', 'high', 'xhigh', 'max', 'ultra'}


def validate_profiles(value):
    if not isinstance(value, dict) or set(value) != set(DEFAULT_PROFILES):
        raise ValueError('profiles must contain exactly orchestrator, implementer and reviewer')
    for role, profile in value.items():
        if not isinstance(profile, dict) or set(profile) != {'id', 'effort'}:
            raise ValueError(role + ' requires exactly id and effort')
        model, effort = profile['id'], profile['effort']
        if not isinstance(model, str) or re.fullmatch(r'[A-Za-z0-9][A-Za-z0-9._:/-]{0,127}', model) is None:
            raise ValueError(role + ' requires a nonempty model identifier without whitespace')
        if not isinstance(effort, str) or effort not in EFFORTS:
            raise ValueError(role + ' has an unsupported reasoning effort')
    return copy.deepcopy(value)
