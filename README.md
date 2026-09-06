# Destiny 1 Reversal

A loss-preserving reverse-engineering workspace for Destiny 1 Tiger packages and asset export.

## Canonical repository

The authoritative, durable workspace is the private GitHub repository `lizardpeter/destiny-1`. ChatGPT/container copies under `/mnt/data/Destiny1_Reversal/` are working mirrors used for binary analysis and generated artifacts. Confirmed documentation, source, tests, and lightweight reproducibility evidence should be committed back to GitHub after each material finding. Raw Destiny package bytes and proprietary Oodle DLLs must never be committed.

## Rules

1. Binary evidence outranks inherited assumptions.
2. Every field/class is labeled by evidence level: `CONFIRMED_BINARY`, `CONFIRMED_CROSS_SOURCE`, `SOURCE_DERIVED`, `STRONGLY_SUPPORTED`, `HYPOTHESIS`, or `UNKNOWN`.
3. Unknown fields remain in the unknown-field ledger until directly resolved.
4. Every analyzed package gets a SHA-256 fingerprint, structural probe, graph/statistics evidence, and regression vectors.
5. PS4 is the canonical extraction corpus; Xbox One is the differential-validation corpus.
6. Export code preserves decoded metadata/hashes alongside converted GLB/DDS/PNG/etc.
7. Proprietary Oodle DLLs are user-supplied at runtime and are never bundled into this workspace.
8. Every material reversal also updates the durable structured knowledge layer. Proven relations, unresolved candidates, evidence provenance, rejected hypotheses, and next-proof frontiers must be retained so later work can query and extend them instead of rediscovering them.

## Current milestone

The payload pipeline is operational:

```text
Tiger package / patch family
    -> verify stored block SHA-1
    -> Oodle 3 decompression
    -> reconstruct logical entry
    -> decode resource/tag header
    -> follow resource graph
    -> texture GCN deswizzle / buffer decode / shader parse
    -> DDS + PNG / proof GLB / JSON evidence
```

Canonical PS4 `arch_cabal_005b_1` currently yields:
- 30/30 Texture2D headers exported to DDS + PNG.
- six position/topology proof GLBs from validated vertex/index groups.
- seven native PS4 GCN PixelShader payloads with parsed `OrbShdr` footers.
- 122 subtype-7 GPU headers with exact `unit_count * 16 == payload_size` relation.

## Canonical files

- `STATUS.md` — current project state and next milestones.
- `spec/D1_TIGER_PACKAGE_v24.md` — living package specification.
- `spec/D1_RESOURCE_CLASSES.md` — resource type/class map.
- `spec/D1_GPU_RESOURCES.md` — decompressed GPU-resource layouts and invariants.
- `spec/d1_tiger_v24.machine.json` — machine-readable schema snapshot.
- `findings/LOG.md` — append-only research log.
- `findings/UNKNOWN_FIELD_LEDGER.md` — unresolved items.
- `corpus/CORPUS.json` — sample inventory and fingerprints/status.
- `notes/OODLE_RUNTIME.md` — Oodle runtime/bridge policy and validation.
- `evidence/` — reproducible outputs derived from package bytes.
- `knowledge/` — canonical structured asset/entity/relation/evidence knowledge records; generated SQLite is built from these records.
- `knowledge/README.md` — knowledge-base policy, proof states, negative-knowledge rules, and query examples.
- `knowledge/schema_v1.json` — machine-readable knowledge record schema.
- `tools/d1_knowledge_db.py` — validator and deterministic JSON-to-SQLite materializer.
- `exports/` — converted preview assets and proof geometry.
- `tools/` — parsers, extractors and comparators.
- `tests/` — regression vectors and self-tests.

## Reproducibility

Package layer:

```bash
python tools/d1_pkg_probe.py <pkg> --full-entries --verify-blocks -o evidence/packages/<name>.probe.json
python tools/analyze_pkg_graph.py evidence/packages/<name>.probe.json evidence/analysis/<name>/
python tools/compare_pkg_reports.py <ps4.report.json> <xbox.report.json> -o diff.json --markdown diff.md
```

Linux Oodle bridge (requires a user-owned `oo2core_3_win64.dll`):

```bash
tools/build_linoodle_min.sh
export OODLE_DLL=/path/to/oo2core_3_win64.dll
export LINOODLE_SKIP_DLLMAIN=1
python tools/d1_oodle_probe.py <pkg> --runtime tools/runtime/linux-x86_64/liblinoodle3_min.so --count 12
```

Bulk PS4 texture extraction:

```bash
python tools/d1_texture_export.py <ps4_pkg> \
  --runtime tools/runtime/linux-x86_64/liblinoodle3_min.so \
  --all --out exports/textures/all_ps4 \
  --manifest evidence/decoded/ps4_texture_manifest.json
```

Knowledge database:

```bash
python tools/d1_knowledge_db.py --records knowledge/records --validate-only
python tools/d1_knowledge_db.py --records knowledge/records --db build/d1_knowledge.sqlite --summary build/d1_knowledge_summary.json
```

Regression suite:

```bash
pytest -q
```
