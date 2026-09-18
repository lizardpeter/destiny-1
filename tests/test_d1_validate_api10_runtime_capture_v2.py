#!/usr/bin/env python3
"""Regression tests for the v2 API10 exact-membership gate."""
import importlib.util, json, tempfile
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
P=ROOT/'tools'/'d1_validate_api10_runtime_capture_v2.py'
spec=importlib.util.spec_from_file_location('v2',P)
v2=importlib.util.module_from_spec(spec); spec.loader.exec_module(v2)

assert v2.CENSUS_SHA256=='7305071b52d427a7cc78da79fe795ca490fcf9edc05c06fbf1cc1c02ab9bfce8'
assert v2.COUNTS=={3,6,8,12}
assert v2.WINDOWS=={'s[12:15]','s[8:11]'}

# A structurally plausible fabricated census must fail before any identities are
# trusted: raw producer-output SHA-256 is the first gate.
with tempfile.TemporaryDirectory() as td:
    p=Path(td)/'fake.json'
    p.write_text(json.dumps({'programs':[{
        'gcn_sha256':f'{i:064x}',
        'descriptor_window':'s[8:11]',
        'tbuffer_instruction_count':8
    } for i in range(39)]}))
    try:
        v2.load_exact_membership(p)
    except SystemExit as e:
        assert 'membership census sha256 does not match frozen producer output' in str(e)
    else:
        raise AssertionError('fabricated census bypassed frozen SHA-256 gate')

# The checked-in provenance summary is deliberately not a substitute for the
# frozen census bytes; it must fail the same gate.
prov=ROOT/'evidence'/'d1_localshader_api10_membership_provenance_v1.json'
try:
    v2.load_exact_membership(prov)
except SystemExit as e:
    assert 'membership census sha256 does not match frozen producer output' in str(e)
else:
    raise AssertionError('provenance summary was incorrectly accepted as census')

print('API10_RUNTIME_CAPTURE_V2_MEMBERSHIP_GATE_GREEN')
