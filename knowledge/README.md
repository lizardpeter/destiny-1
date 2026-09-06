# Destiny 1 reverse-engineering knowledge base

This directory is the canonical, Git-friendly knowledge layer for the project.

The rule is simple: every meaningful reversal should leave behind both:

1. executable proof/extraction code, and
2. structured durable knowledge that records what is known, why it is known, what was rejected, and what remains unresolved.

The generated SQLite database is a convenience view. The committed JSON records are the source of truth.

## Why JSON source + generated SQLite

Binary SQLite files are poor review artifacts in Git. The canonical records therefore remain ordinary JSON under `knowledge/records/`, while `tools/d1_knowledge_db.py` validates them and materializes a queryable SQLite database.

This gives us both properties we want:

- exact reviewable diffs and durable provenance in Git;
- fast queries across assets, TagHashes, models, skeletons, activities, packages, names, animations, textures, shaders, and evidence.

## Record model

Each `knowledge/records/*.json` document uses `d1_knowledge_record/v1` and contains:

- `nodes`: things that exist or are being investigated;
- `edges`: typed relationships between nodes;
- `assertions`: explicit claims with proof state and evidence;
- `sources`: provenance for reports, retail-byte scans, repository files, Actions artifacts, manifest snapshots, and source-pinned external implementations;
- `rejections`: negative knowledge such as a candidate proven not to be the target;
- `frontiers`: unresolved questions and the exact next proof needed.

Node IDs are stable semantic identifiers, not row numbers. Examples:

- `entity:8108EFFC`
- `model:8108F1AD`
- `skeleton:8108F021`
- `activity:810B0002`
- `scenario:8108E004`
- `semantic:crota_son_of_oryx`

## Proof states

The allowed proof states are deliberately explicit:

- `PROVEN`: exact source/retail-byte ownership or equality is closed;
- `STRONGLY_SUPPORTED`: multiple exact observations support the claim, but the final semantic ownership edge is not closed;
- `CANDIDATE`: worth investigating, not promoted;
- `UNRESOLVED`: known object or relation whose meaning is not yet closed;
- `REJECTED`: a previously plausible candidate has been disproven;
- `TARGET`: semantic target being sought; this is not a binary identity claim.

`PROVEN` must never be assigned from visual resemblance, package-name proximity, model size, skeleton size, neighboring entry order, or intuition.

## Negative knowledge is first-class

Rejected candidates are kept permanently when the rejection is useful. A later tool should be able to ask not only:

> Which entity is Crota?

but also:

> Which entities were considered for Crota, which ones were rejected, and what exact evidence rejected them?

This prevents rediscovery loops and accidental regression to old guesses.

## Source durability

Temporary Actions artifacts may expire. Important claims therefore record:

- the artifact ID when useful;
- the artifact ZIP SHA-256;
- the SHA-256 of the important report inside the artifact;
- the producing tool/workflow/commit when available;
- enough summarized exact values in the knowledge record to preserve the finding after artifact expiry.

Large raw reports can remain ephemeral when their important closed facts have been promoted into the knowledge base with hashes and provenance.

## Build and validate

```bash
python tools/d1_knowledge_db.py --records knowledge/records --validate-only
python tools/d1_knowledge_db.py --records knowledge/records --db build/d1_knowledge.sqlite --summary build/d1_knowledge_summary.json
```

CI runs the same validator and publishes a generated `d1_knowledge.sqlite` artifact.

## Query examples

```sql
-- Everything that uses one skeleton
SELECT e.subject_id, e.predicate, e.object_id, e.status
FROM edges e
WHERE e.object_id = 'skeleton:8108F021';

-- Why a Crota candidate was rejected
SELECT r.candidate_node_id, r.rejected_as, r.reason
FROM rejections r
WHERE r.record_id = 'crota_end_2026_09_06';

-- Claims that are not yet proven
SELECT record_id, assertion_id, status, claim
FROM assertions
WHERE status IN ('CANDIDATE','UNRESOLVED','STRONGLY_SUPPORTED');
```

## Project policy

Every future asset reversal should update this layer when it establishes durable knowledge. That includes maps, entities, enemies, NPCs, Guardians, weapons, materials, shaders, textures, skeletons, animation controllers, clips, package schemas, class layouts, and rejected hypotheses.
