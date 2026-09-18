#!/usr/bin/env python3
"""Unit checks for API10 primary/semantic provenance helpers.

These use synthetic hashes only to exercise validator policy.  They are not
runtime evidence and assert no Destiny engine semantic.
"""
import importlib.util
from pathlib import Path

P=Path(__file__).parents[1]/"tools"/"d1_localshader_api10_capture_gate_v1.py"
spec=importlib.util.spec_from_file_location("gate",P); gate=importlib.util.module_from_spec(spec);spec.loader.exec_module(gate)
H0="00"*32; H1="11"*32

def must_fail(fn,needle):
    try:fn()
    except SystemExit as e:
        assert needle in str(e),(needle,str(e));return
    raise AssertionError("expected fail-closed rejection")

gate.require_primary_evidence({"source":"capture.bin","sha256":H0})
must_fail(lambda:gate.require_primary_evidence({"source":"capture.bin","sha256":"bad"}),"64 hex digits")
must_fail(lambda:gate.require_primary_evidence({"source":"","sha256":H0}),"non-empty source")

good={"writer_trace":{"source":"writer.trace","sha256":H0},"backing_bytes":{"source":"backing.bin","sha256":H1}}
gate.require_semantic_provenance(good,0)
must_fail(lambda:gate.require_semantic_provenance({"writer_trace":"truthy","backing_bytes":"truthy"},0),"must be an object")
must_fail(lambda:gate.require_semantic_provenance({"writer_trace":{"source":"same.bin","sha256":H0},"backing_bytes":{"source":"same.bin","sha256":H0}},0),"must be distinct")
must_fail(lambda:gate.require_semantic_provenance({"writer_trace":{"source":"w","sha256":H0},"backing_bytes":{"source":"b","sha256":"bad"}},0),"64 hex digits")
print("PASS: API10 provenance policy rejects opaque/truthy/unhashed semantic evidence")
