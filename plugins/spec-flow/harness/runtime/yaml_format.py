"""Bounded YAML contract codec: JSON-compatible data, no implicit YAML 1.1 types."""
import json
import re
from typing import Any
from .._vendor import yaml


class StrictLoader(yaml.SafeLoader):
    yaml_implicit_resolvers: dict[Any, Any] = {}

    def __init__(self, stream):
        super().__init__(stream)
        self.contract_depth = 0
        self.contract_nodes = 0

    def compose_node(self, parent, index):
        event = self.peek_event()
        if isinstance(event, yaml.AliasEvent) or getattr(event, 'anchor', None) or getattr(event, 'tag', None):
            raise ValueError('YAML anchors, aliases and explicit tags are not supported')
        self.contract_nodes += 1
        self.contract_depth += 1
        try:
            if self.contract_depth > 64 or self.contract_nodes > 50000:
                raise ValueError('YAML contract exceeds nesting or node limit')
            return super().compose_node(parent, index)
        finally:
            self.contract_depth -= 1

    def construct_mapping(self, node, deep=False):
        result = {}
        for key_node, value_node in node.value:
            key = self.construct_object(key_node, deep=deep)
            if not isinstance(key, str) or key == '<<':
                raise ValueError('YAML mapping keys must be strings; merges are not supported')
            if key in result:
                raise ValueError('duplicate YAML key: ' + key)
            result[key] = self.construct_object(value_node, deep=deep)
        return result


for tag, pattern, first in (
    ('bool', r'^(?:true|false)$', 'tf'),
    ('null', r'^(?:null|~)$', 'n~'),
    ('int', r'^-?(?:0|[1-9][0-9]*)$', '-0123456789'),
    ('float', r'^-?(?:0|[1-9][0-9]*)(?:\.[0-9]+(?:[eE][-+]?[0-9]+)?|[eE][-+]?[0-9]+)$', '-0123456789'),
):
    StrictLoader.add_implicit_resolver('tag:yaml.org,2002:' + tag, re.compile(pattern), list(first))


def load_contract(text):
    if len(text.encode('utf-8')) > 4 * 1024 * 1024:
        raise ValueError('YAML contract exceeds 4 MiB')
    try:
        value = yaml.load(text, Loader=StrictLoader)
        # Also reject infinities produced by exponent overflow.
        json.dumps(value, allow_nan=False)
        return value
    except (yaml.YAMLError, TypeError, OverflowError, RecursionError) as exc:
        raise ValueError('invalid YAML contract: ' + str(exc)) from exc


class ContractDumper(yaml.SafeDumper):
    def ignore_aliases(self, data):
        return True

    # Quote values which a downstream YAML reader might interpret differently.
    yaml_implicit_resolvers = {key: list(value) for key, value in yaml.SafeDumper.yaml_implicit_resolvers.items()}


# The emitter must quote every string which either the strict reader or a
# conventional YAML reader would implicitly type (notably "1e2").
for first, resolvers in StrictLoader.yaml_implicit_resolvers.items():
    for tag, regexp in resolvers:
        ContractDumper.add_implicit_resolver(tag, regexp, [first])


def dump_contract(contract):
    return yaml.dump(contract, Dumper=ContractDumper, allow_unicode=True,
                     sort_keys=False, default_flow_style=False, width=100).rstrip('\n')
