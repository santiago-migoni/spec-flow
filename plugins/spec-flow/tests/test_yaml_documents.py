"""Document-format compatibility and strict YAML boundary regressions."""
import hashlib
import json
import tempfile
import unittest
from pathlib import Path
from harness.runtime.contracts import ContractError, read_document, document_digest, render_document, read_document_text, replace_contract

HEADER = '---\nschema_version: 1\nkind: constitution\nrevision: R00\nid: CONST-TEST\ndepends_on: []\n---\n\n# Decision\n\nApproved purpose.\n'

class YAMLDocumentTests(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory()
        self.addCleanup(self.tmp.cleanup)
        self.path = Path(self.tmp.name) / 'constitution.md'

    def write(self, text):
        self.path.write_text(text)
        return self.path

    def test_yaml_header_is_read_as_contract_not_prose(self):
        doc = read_document(self.write(HEADER))
        self.assertEqual(doc['contract']['schema_version'], 1)
        self.assertEqual(doc['contract']['depends_on'], [])
        self.assertEqual(doc['prose'], '# Decision\n\nApproved purpose.')

    def test_legacy_digest_is_exactly_preserved(self):
        data = {'schema_version': 1, 'kind': 'constitution', 'revision': 'R00', 'id': 'CONST-TEST', 'depends_on': []}
        text = '# Decision\n\n```spec-flow\n' + json.dumps(data, indent=2) + '\n```\n\nPurpose.\n'
        expected = text[:text.index('```spec-flow')] + '```spec-flow\n' + json.dumps(data, ensure_ascii=False, sort_keys=True, separators=(',', ':')) + '\n```\n\nPurpose.\n'
        self.assertEqual(document_digest(self.write(text)), hashlib.sha256(expected.encode()).hexdigest())

    def test_yaml_digest_ignores_status_and_generated_progress_only(self):
        first = document_digest(self.write(HEADER))
        text = HEADER.replace('kind: constitution', 'status: draft\nkind: constitution')
        self.assertEqual(document_digest(self.write(text)), first)
        text += '\n<!-- spec-flow:generated:start -->\nProgress view maintained by the harness.\n<!-- spec-flow:generated:end -->\n'
        self.assertEqual(document_digest(self.write(text)), first)
        self.assertNotEqual(document_digest(self.write(HEADER.replace('Approved purpose.', 'Changed purpose.'))), first)

    def test_invalid_or_ambiguous_yaml_is_rejected(self):
        cases = [HEADER.replace('kind: constitution', 'kind: constitution\nkind: spec'),
                 HEADER + '\n```spec-flow\n{}\n```\n',
                 HEADER.replace('depends_on: []', 'depends_on: &pins []'),
                 HEADER.replace('depends_on: []', 'depends_on: *pins'),
                 HEADER.replace('id: CONST-TEST', 'id: !!str CONST-TEST'),
                 HEADER.replace('id: CONST-TEST', '7: value'),
                 HEADER.replace('---\n\n# Decision', '\n# Decision'),
                 HEADER.replace('id: CONST-TEST', 'id: [unterminated'),
                 HEADER.replace('id: CONST-TEST', 'id: CONST-TEST\n...\nkind: second'),
                 HEADER.replace('depends_on: []', 'depends_on: {path: a, path: b}'),
                 HEADER.replace('kind: constitution', '# <!-- spec-flow:generated:start -->\nkind: constitution')]
        for text in cases:
            with self.subTest(text=text), self.assertRaises(ContractError):
                read_document(self.write(text))

    def test_yaml_plain_strings_do_not_become_dates_or_legacy_booleans(self):
        for value in ['yes', 'no', 'on', '2026-10-16', 'R00']:
            self.assertEqual(read_document(self.write(HEADER.replace('CONST-TEST', value)))['contract']['id'], value)

    def test_nested_records_and_ambiguous_strings_round_trip(self):
        values = ['yes', 'no', 'true', 'null', '1e2', '1E-2', '001', '0x10', '2026-10-16', '~', '', 'á: # título', 'line one\nline two']
        contract = {'schema_version': 1, 'kind': 'tasks', 'records': [
            {'id': value, 'number': 100.0, 'enabled': False, 'nothing': None, 'argv': ['python3', '-c', value]}
            for value in values]}
        contract['records'].append(contract['records'][0])
        self.assertEqual(read_document_text(render_document(contract, 'Decision.'))['contract'], contract)

    def test_rejects_resource_overflow_nonfinite_and_generated_in_header(self):
        for text in (HEADER.replace('CONST-TEST', '1e9999'),
                     HEADER.replace('depends_on: []', 'depends_on: ' + '[' * 70 + '0' + ']' * 70),
                     HEADER.replace('kind: constitution', '# <!-- spec-flow:generated:start -->\nkind: constitution')):
            with self.subTest(text=text), self.assertRaises(ContractError):
                document_digest(self.write(text))
