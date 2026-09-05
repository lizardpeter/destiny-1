from __future__ import annotations

import struct

from tools.d1_character_owner_backlinks import scan_aligned_targets, summarize_sources


def test_aligned_target_scan_rejects_unaligned_occurrence():
    targets = {0x816CE092: "816CE092", 0x816CE095: "816CE095"}
    payload = bytearray(20)
    struct.pack_into("<I", payload, 4, 0x816CE092)
    # Literal bytes exist, but deliberately not on a dword boundary.
    payload[11:15] = struct.pack("<I", 0x816CE095)

    hits = scan_aligned_targets(bytes(payload), targets)

    assert hits == [{"offset": 4, "target": "816CE092"}]


def test_summary_preserves_exact_offsets_and_cooccurrence():
    rows = [
        {
            "source": {"tag_hash": "AAAA0001", "reference": "80800861"},
            "hits": [
                {"offset": 16, "target": "816CE092"},
                {"offset": 24, "target": "816CE095"},
                {"offset": 40, "target": "816CE092"},
            ],
        },
        {
            "source": {"tag_hash": "AAAA0002", "reference": "808005A1"},
            "hits": [{"offset": 8, "target": "816CE09D"}],
        },
    ]

    out = summarize_sources(rows, ["816CE092", "816CE095", "816CE09D"])

    assert out["backlinks"]["816CE092"][0]["offsets"] == [16, 40]
    assert out["backlinks"]["816CE092"][0]["cooccurring_targets"] == ["816CE095"]
    assert out["backlinks"]["816CE095"][0]["cooccurring_targets"] == ["816CE092"]
    assert out["backlinks"]["816CE09D"][0]["cooccurring_targets"] == []
    assert out["cooccurrence_groups"] == [
        {"targets": ["816CE092", "816CE095"], "source_count": 1}
    ]
