#!/usr/bin/env python3
"""Offline regression checks of the actual research parser source.

Load only its parsing definitions through AST so these checks do not need the
remote corpus transport dependencies or downloaded packages. The bodies under
test are not copied or replaced.
"""
from __future__ import annotations
import ast
import hashlib
import struct
import unittest
from pathlib import Path

SOURCE = Path(__file__).with_name("d1_remote_activity_audio_composition_closure.py")
RETAIL_HEX = "50000000000000008811ef51d4e31648000000000000000000000000000000000000000000000000000000000000000001d4aa801281c98000000000000000000000000000000000ffffffff00000000"
NAMES = {"norm", "u32", "i32", "i64", "u64", "dyn", "meta_row", "exact", "parse_event"}
module = ast.parse(SOURCE.read_text())
nodes = [node for node in module.body if isinstance(node, ast.FunctionDef) and node.name in NAMES]
if {node.name for node in nodes} != NAMES:
    raise RuntimeError("parser definition set drift")
namespace = {
    "hashlib": hashlib, "struct": struct,
    "WWISE_EVENT_REF": "8080080A", "WWISE_STREAM_TYPE": 8, "WWISE_STREAM_SUBTYPE": 21,
    "NULLS": {"00000000", "FFFFFFFF"},
}
# The original source uses postponed annotations.
prefix = ast.parse("from __future__ import annotations").body
exec(compile(ast.fix_missing_locations(ast.Module(body=prefix + nodes, type_ignores=[])),
             str(SOURCE), "exec"), namespace)

class Corpus:
    def __init__(self, payload):
        self.payloads = {"80C9808E": payload}
        self.metadata = {"80C9808E": {"tag_hash": "80C9808E", "reference": "8080080A"},
                         "80C98112": {"tag_hash": "80C98112"}}
    def entry_meta(self, tag):
        return self.metadata.get(tag)
    def payload(self, tag):
        return self.payloads.get(tag), "offline-exact-fixture"

class EventContract(unittest.TestCase):
    def parse(self, payload, setup=None):
        corpus = Corpus(payload)
        if setup:
            setup(corpus)
        return namespace["parse_event"](corpus, "80C9808E", {})

    def test_exact_short_retail_bank_only_event(self):
        payload = bytes.fromhex(RETAIL_HEX)
        self.assertEqual(len(payload), 0x50)
        self.assertEqual(hashlib.sha256(payload).hexdigest(),
            "2334e171999242c2bb32c2cddb66b72e624a4b5b32d093eaa5694f96d567d31c")
        row = self.parse(payload)
        self.assertTrue(row["validation_ok"])
        self.assertEqual(row["bank_tag_hash"], "80C98112")
        self.assertEqual(row["streams"], [])

    def test_empty_array_ignores_extreme_pointer(self):
        payload = bytearray.fromhex(RETAIL_HEX)
        struct.pack_into("<q", payload, 0x40, (1 << 63) - 1)
        self.assertTrue(self.parse(payload)["validation_ok"])

    def test_relocated_array_and_unrelated_descriptor_word(self):
        payload = bytearray(0x58)
        struct.pack_into("<iiqII", payload, 0x38, 2, 0x1234, 0, 0, 0)
        struct.pack_into("<II", payload, 0x50, 0x80805678, 0xffffffff)
        def setup(c):
            c.metadata["80805678"] = {"tag_hash": "80805678", "type": 8, "subtype": 21}
            c.payloads["80805678"] = b"owned stream bytes"
        row = self.parse(payload, setup)
        self.assertTrue(row["validation_ok"])
        self.assertEqual(row["stream_count"], 2)
        self.assertEqual(row["streams"][0]["field_offset"], 0x50)
        self.assertTrue(row["streams"][1]["is_null"])

    def test_negative_count_rejected(self):
        payload = bytearray.fromhex(RETAIL_HEX)
        struct.pack_into("<i", payload, 0x38, -1)
        self.assertIn("event_stream_descriptor_invalid", self.parse(payload)["violations"])

    def test_nonempty_array_out_of_bounds_rejected(self):
        for relative in (-(1 << 63), (1 << 63) - 1, 0):
            payload = bytearray.fromhex(RETAIL_HEX)
            struct.pack_into("<i", payload, 0x38, 1)
            struct.pack_into("<q", payload, 0x40, relative)
            self.assertIn("event_stream_descriptor_invalid", self.parse(payload)["violations"])

    def test_truncated_descriptor_rejected(self):
        self.assertIn("event_bank_stream_descriptor_oob",
                      self.parse(bytes(0x47))["violations"])

    def test_wrong_stream_type_rejected(self):
        payload = bytearray(0x54)
        struct.pack_into("<i", payload, 0x38, 1)
        struct.pack_into("<I", payload, 0x50, 0x80805678)
        def setup(c):
            c.metadata["80805678"] = {"type": 8, "subtype": 20}
        self.assertIn("stream_0_80805678_type_subtype_8_20",
                      self.parse(payload, setup)["violations"])

    def test_missing_stream_bytes_rejected(self):
        payload = bytearray(0x54)
        struct.pack_into("<i", payload, 0x38, 1)
        struct.pack_into("<I", payload, 0x50, 0x80805678)
        def setup(c):
            c.metadata["80805678"] = {"type": 8, "subtype": 21}
        self.assertTrue(self.parse(payload, setup)["violations"])

if __name__ == "__main__":
    unittest.main()
