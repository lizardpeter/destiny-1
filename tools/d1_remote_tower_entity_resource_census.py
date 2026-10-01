#!/usr/bin/env python3
"""Census exact current-retail D1 Tower map-owned entity resources remotely.

Traversal is source-pinned and loss-preserving:

  SMapDataEntry.entity_hash
    -> D1 SEntity / canonical 80800734
       +0x20 DynamicArray<D1 entity-resource entry>, stride 0x0C
          +0x00 FileHash Resource
    -> D1 EntityResource / canonical 80800861
       -> exact ResourcePointer classes at +0x08/+0x10/+0x18

This tool does not guess which discriminator is the global-channel sequencer.
It reports every raw current-retail Unk10/Unk18 class with owner entities so a
later structural/source join can identify the relevant family.

Input map-data-layer JSON should be produced by d1_world_map_data_layer_census.py.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import re
import struct
import sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from d1_entity_resource_probe import ENTITY_RESOURCE_CLASS, parse_resource, resource_ptr
from d1_investment_arrangement_probe import dyn_header, filehash_pkg_index
from d1_remote_investment_parent_probe import RemoteLogicalPackage, parse_member
from d1_split_tar_extract import SplitHttpTar

ENTITY_CLASS = "80800734"
# Rhys-Kovacevic/charm_exporter@4bdce747... D1-specific schemas:
#   S79818080: source bytes "10068080" -> parsed little-endian class 0x80800610
#   SD1918080: source bytes "07058080" -> parsed class 0x80800507
#   S6F818080 ID row: source bytes "88078080", embedded array row
D1_GLOBAL_CHANNEL_DISCRIMINATOR_CLASS = "8080079A"
D1_GLOBAL_CHANNEL_PARENT_CLASS = "80800610"
D1_GLOBAL_CHANNEL_ENTRY_CLASS = "80800507"
REQUESTED_LIGHT_CHANNELS = {0x11, 0x28, 0x30, 0x60}
NULLS = {"00000000", "FFFFFFFF"}


def norm(x: object) -> str:
    s = str(x).upper().removeprefix("0X").zfill(8)
    int(s, 16)
    return s


def current_family_names(package_list: Path, pkgid: int) -> list[str]:
    token = f"{pkgid:04x}"
    out = []
    for line in package_list.read_text(errors="replace").splitlines():
        name = Path(line.strip()).name
        if re.search(rf"_{token}_[0-9]+\.pkg$", name, re.I):
            out.append(name)
    return sorted(set(out))


class RemoteCorpus:
    def __init__(
        self,
        archive: SplitHttpTar,
        package_list: Path,
        runtime: Path,
    ) -> None:
        self.archive = archive
        self.package_list = package_list
        self.runtime = runtime
        self.views: dict[int, RemoteLogicalPackage] = {}
        self.package_rows: dict[int, dict] = {}

    def ensure(self, pkgids: set[int]) -> None:
        missing_ids = sorted(pkg for pkg in pkgids if pkg not in self.views)
        if not missing_ids:
            return

        names_by_pkg: dict[int, list[str]] = {}
        all_names: set[str] = set()
        for pkg in missing_ids:
            names = current_family_names(self.package_list, pkg)
            row = {
                "package_id": f"{pkg:04X}",
                "current_members": names,
                "member_locations": {},
                "violations": [],
            }
            self.package_rows[pkg] = row
            if not names:
                row["violations"].append("package_family_absent_from_packages_list")
                continue
            names_by_pkg[pkg] = names
            all_names.update(names)

        if not all_names:
            return

        found, headers = self.archive.find(all_names)
        for pkg, names in names_by_pkg.items():
            row = self.package_rows[pkg]
            row["tar_headers_scanned"] = headers
            missing = sorted(set(names) - set(found))
            if missing:
                row["violations"].append(
                    "archive_members_missing:" + ",".join(missing)
                )
                continue
            specs = []
            for name in names:
                loc = found[name]
                row["member_locations"][name] = loc
                specs.append(
                    parse_member(
                        f"{name}:0x{int(loc['data_offset']):X}:{int(loc['size'])}"
                    )
                )
            try:
                view = RemoteLogicalPackage(
                    self.archive,
                    {m.patch_id: m for m in specs},
                    self.runtime,
                )
                self.views[pkg] = view
                row["logical_view"] = view.view.name
                row["entry_count"] = len(view.entries)
                row["block_count"] = len(view.blocks)
            except Exception as ex:
                row["violations"].append("logical_package_build:" + repr(ex))

    def payload(self, tag_hash: str) -> tuple[dict | None, bytes | None, str | None]:
        h = norm(tag_hash)
        pkg, idx = filehash_pkg_index(int(h, 16))
        view = self.views.get(pkg)
        if view is None:
            return None, None, "package_view_unavailable"
        if idx >= len(view.entries):
            return None, None, "file_index_outside_current_entry_table"
        e = view.entries[idx]
        if norm(e["tag_hash"]) != h:
            return e, None, "logical_tag_hash_mismatch"
        try:
            return e, view.entry(idx), None
        except Exception as ex:
            return e, None, "payload_read:" + repr(ex)


def map_entity_owners(doc: dict) -> dict[str, list[dict]]:
    owners: dict[str, list[dict]] = defaultdict(list)
    for table in doc.get("tables", []):
        table_hash = norm(table.get("map_data_table", "0"))
        for row in table.get("entries", []):
            h = norm(row.get("entity_hash", "0"))
            if h in NULLS:
                continue
            owners[h].append(
                {
                    "map_data_table": table_hash,
                    "map_entry_index": row.get("index"),
                    "world_id": row.get("world_id"),
                    "translation": row.get("translation"),
                    "resource_class": row.get("resource_class"),
                }
            )
    return dict(owners)


def parse_entity_resources(payload: bytes) -> dict:
    count, data = dyn_header(payload, 0x20)
    end = data + count * 0x0C
    if count < 0 or data < 0 or end > len(payload):
        raise ValueError(
            f"EntityResources out of bounds: count={count} data=0x{data:X} "
            f"end=0x{end:X} size=0x{len(payload):X}"
        )
    rows = []
    for i in range(count):
        off = data + i * 0x0C
        resource = struct.unpack_from("<I", payload, off)[0]
        rows.append(
            {
                "index": i,
                "record_offset": off,
                "record_offset_hex": f"0x{off:X}",
                "resource_hash": f"{resource:08X}",
                "record_hex": payload[off : off + 0x0C].hex().upper(),
            }
        )
    return {
        "count": count,
        "data_offset": data,
        "data_offset_hex": f"0x{data:X}",
        "end_offset": end,
        "end_offset_hex": f"0x{end:X}",
        "stride": 0x0C,
        "rows": rows,
    }


def decode_vec4(payload: bytes, off: int) -> list[float]:
    if off < 0 or off + 16 > len(payload):
        raise ValueError(f"Vec4 OOB at 0x{off:X}")
    return list(struct.unpack_from("<4f", payload, off))


def decode_global_channel_parent(payload: bytes, parent: int) -> dict:
    """Decode source-pinned D1 global-channel parent arrays from one EntityResource."""
    if parent < 0 or parent + 0x150 > len(payload):
        raise ValueError(
            f"global-channel parent header OOB: 0x{parent:X}/0x{len(payload):X}"
        )

    arrays = []
    wrappers = []
    for name, rel_off in (
        ("array1", 0x110),
        ("array2", 0x120),
        ("d1_array3", 0x130),
    ):
        field = parent + rel_off
        count, data = dyn_header(payload, field)
        end = data + count * 8
        if count < 0 or data < 0 or end > len(payload):
            raise ValueError(
                f"{name} OOB count={count} data=0x{data:X} end=0x{end:X}"
            )
        arr = {
            "name": name,
            "field_offset": field,
            "field_offset_hex": f"0x{field:X}",
            "count": count,
            "data_offset": data,
            "data_offset_hex": f"0x{data:X}",
            "stride": 8,
        }
        arrays.append(arr)
        for i in range(count):
            off = data + i * 8
            ptr = resource_ptr(payload, off)
            wrappers.append({
                "array": name,
                "index": i,
                "record_offset": off,
                "record_offset_hex": f"0x{off:X}",
                "pointer": ptr,
            })

    id_field = parent + 0x140
    id_count, id_data = dyn_header(payload, id_field)
    id_end = id_data + id_count * 0x30
    if id_count < 0 or id_data < 0 or id_end > len(payload):
        raise ValueError(
            f"channel ID array OOB count={id_count} data=0x{id_data:X} end=0x{id_end:X}"
        )
    ids = []
    for i in range(id_count):
        off = id_data + i * 0x30
        channel_id = struct.unpack_from("<I", payload, off + 0x28)[0]
        ids.append({
            "index": i,
            "string_hash": f"{channel_id:08X}",
            "record_offset": off,
            "record_offset_hex": f"0x{off:X}",
        })

    programs = []
    unknown_target_classes = Counter()
    for wrapper in wrappers:
        ptr = wrapper["pointer"]
        cls = ptr.get("class_hash")
        if cls != D1_GLOBAL_CHANNEL_ENTRY_CLASS:
            if cls:
                unknown_target_classes[cls] += 1
            continue
        target = ptr.get("target_offset")
        if not isinstance(target, int) or target + 0x48 > len(payload):
            raise ValueError(f"global channel entry target invalid: {ptr}")

        channel_index = struct.unpack_from("<I", payload, target + 0x20)[0]
        unk14 = struct.unpack_from("<f", payload, target + 0x14)[0]

        byte_count, byte_data = dyn_header(payload, target + 0x28)
        byte_end = byte_data + byte_count
        if byte_count < 0 or byte_data < 0 or byte_end > len(payload):
            raise ValueError(
                f"channel {channel_index} bytecode OOB count={byte_count} data=0x{byte_data:X}"
            )
        value_count, value_data = dyn_header(payload, target + 0x38)
        value_end = value_data + value_count * 16
        if value_count < 0 or value_data < 0 or value_end > len(payload):
            raise ValueError(
                f"channel {channel_index} values OOB count={value_count} data=0x{value_data:X}"
            )

        channel_id = ids[channel_index]["string_hash"] if channel_index < len(ids) else None
        values = [
            decode_vec4(payload, value_data + i * 16)
            for i in range(value_count)
        ]
        bytecode = payload[byte_data:byte_end]
        programs.append({
            "channel_index": channel_index,
            "channel_index_hex": f"0x{channel_index:02X}",
            "channel_id_string_hash": channel_id,
            "entry_offset": target,
            "entry_offset_hex": f"0x{target:X}",
            "unk14": unk14,
            "bytecode_count": byte_count,
            "bytecode_hex": bytecode.hex().upper(),
            "bytecode_sha256": hashlib.sha256(bytecode).hexdigest(),
            "constant_vec4_count": value_count,
            "constant_vec4s": values,
            "is_dynamic_lineage_rule": byte_count > 4,
            "local_channel_index": channel_index,
            "local_channel_index_hex": f"0x{channel_index:02X}",
            "requested_by_tower_light_0x4b": False,
            "requested_by_tower_light_0x4b_note": (
                "Withheld here: SD1918080.ChannelIndex indexes the sequencer-local "
                "S6F818080 ID array. Raw TFX 0x4B indexes the ordered global defaults "
                "table. Join by channel_id_string_hash before comparing indices."
            ),
        })

    # Do not compare local ChannelIndex to raw TFX 0x4B global-table indices.
    # GlobalExporter source joins the local Array3 ID StringHash to
    # GlobalChannelDefaults, then derives the global ordered index.
    requested = []
    return {
        "parent_class": D1_GLOBAL_CHANNEL_PARENT_CLASS,
        "parent_offset": parent,
        "parent_offset_hex": f"0x{parent:X}",
        "program_arrays": arrays,
        "wrapper_count": len(wrappers),
        "id_array": {
            "field_offset": id_field,
            "field_offset_hex": f"0x{id_field:X}",
            "count": id_count,
            "data_offset": id_data,
            "data_offset_hex": f"0x{id_data:X}",
            "stride": 0x30,
        },
        "channel_ids": ids,
        "program_count": len(programs),
        "programs": programs,
        "requested_tower_light_programs": requested,
        "tower_light_join_policy": (
            "requested_tower_light_programs intentionally remains empty until an "
            "exact StringHash join against GlobalChannelDefaults maps each local "
            "program ID to its global ordered index."
        ),
        "unknown_wrapper_target_class_counts": dict(unknown_target_classes),
    }


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--map-data-layer", type=Path, required=True)
    ap.add_argument("--package-list", type=Path, required=True)
    ap.add_argument("--runtime", type=Path, required=True)
    ap.add_argument(
        "--base-url",
        default="https://crypt.cohae.dev/destiny/ps4/packages/latest",
    )
    ap.add_argument("--part-count", type=int, default=10)
    ap.add_argument("--out", type=Path, required=True)
    a = ap.parse_args()

    layer = json.loads(a.map_data_layer.read_text())
    owners = map_entity_owners(layer)
    entity_hashes = sorted(owners)

    base = a.base_url.rstrip("/")
    archive = SplitHttpTar(
        [f"{base}/packages.tar.{i:03d}" for i in range(1, a.part_count + 1)],
        retries=6,
        timeout=120,
    )
    corpus = RemoteCorpus(archive, a.package_list, a.runtime)

    entity_pkgids = {filehash_pkg_index(int(h, 16))[0] for h in entity_hashes}
    corpus.ensure(entity_pkgids)

    entities = []
    resource_owners: dict[str, list[dict]] = defaultdict(list)
    violations = []

    for h in entity_hashes:
        meta, payload, error = corpus.payload(h)
        row = {
            "entity_hash": h,
            "map_owners": owners[h],
            "entry": meta,
            "violations": [],
        }
        if error:
            row["violations"].append(error)
        elif norm(meta.get("reference", "0")) != ENTITY_CLASS:
            row["violations"].append(
                f"class_mismatch:{norm(meta.get('reference','0'))}!={ENTITY_CLASS}"
            )
        else:
            row["payload_size"] = len(payload)
            row["payload_sha256"] = hashlib.sha256(payload).hexdigest()
            try:
                parsed = parse_entity_resources(payload)
                row["entity_resources"] = parsed
                for rr in parsed["rows"]:
                    rh = rr["resource_hash"]
                    if rh in NULLS:
                        continue
                    resource_owners[rh].append(
                        {
                            "entity_hash": h,
                            "entity_resource_index": rr["index"],
                            "map_owners": owners[h],
                        }
                    )
            except Exception as ex:
                row["violations"].append("entity_resource_array:" + repr(ex))
        violations.extend(f"{h}:{x}" for x in row["violations"])
        entities.append(row)

    resource_hashes = sorted(resource_owners)
    resource_pkgids = {filehash_pkg_index(int(h, 16))[0] for h in resource_hashes}
    corpus.ensure(resource_pkgids)

    resources = []
    unk08 = Counter()
    unk10 = Counter()
    unk18 = Counter()
    roles = Counter()
    class_to_resources: dict[str, list[str]] = defaultdict(list)

    for h in resource_hashes:
        meta, payload, error = corpus.payload(h)
        row = {
            "resource_hash": h,
            "owners": resource_owners[h],
            "entry": meta,
            "violations": [],
        }
        if error:
            row["violations"].append(error)
        elif norm(meta.get("reference", "0")) != ENTITY_RESOURCE_CLASS:
            row["violations"].append(
                f"class_mismatch:{norm(meta.get('reference','0'))}!={ENTITY_RESOURCE_CLASS}"
            )
        else:
            row["payload_size"] = len(payload)
            row["payload_sha256"] = hashlib.sha256(payload).hexdigest()
            try:
                parsed = parse_resource(payload, "PS4")
                row["entity_resource"] = parsed
                roles[parsed.get("semantic_role", "other_or_unknown")] += 1
                for field, counter in (
                    ("unk08", unk08),
                    ("unk10", unk10),
                    ("unk18", unk18),
                ):
                    cls = (parsed.get(field) or {}).get("class_hash")
                    if cls:
                        counter[cls] += 1
                        if field == "unk10":
                            class_to_resources[cls].append(h)
            except Exception as ex:
                row["violations"].append("entity_resource_parse:" + repr(ex))
        violations.extend(f"{h}:{x}" for x in row["violations"])
        resources.append(row)

    global_channel_parents = []
    for row in resources:
        parsed = row.get("entity_resource")
        if not parsed:
            continue
        p18 = parsed.get("unk18") or {}
        p10 = parsed.get("unk10") or {}
        if (
            p10.get("class_hash") != D1_GLOBAL_CHANNEL_DISCRIMINATOR_CLASS
            or p18.get("class_hash") != D1_GLOBAL_CHANNEL_PARENT_CLASS
        ):
            continue
        target = p18.get("target_offset")
        try:
            decoded = decode_global_channel_parent(
                # Recover the already fetched payload exactly once more through corpus.
                corpus.payload(row["resource_hash"])[1],
                int(target),
            )
            global_channel_parents.append({
                "resource_hash": row["resource_hash"],
                "owners": row["owners"],
                "decoded": decoded,
            })
        except Exception as ex:
            row["violations"].append("global_channel_parent_decode:" + repr(ex))
            violations.append(
                f'{row["resource_hash"]}:global_channel_parent_decode:{repr(ex)}'
            )

    candidate_classes = []
    for cls, count in sorted(unk10.items(), key=lambda kv: (-kv[1], kv[0])):
        rhs = sorted(set(class_to_resources.get(cls, [])))
        owner_entities = sorted(
            {
                owner["entity_hash"]
                for rh in rhs
                for owner in resource_owners.get(rh, [])
            }
        )
        candidate_classes.append(
            {
                "unk10_class": cls,
                "resource_count": count,
                "resource_hashes": rhs,
                "owner_entity_count": len(owner_entities),
                "owner_entities": owner_entities,
            }
        )

    out = {
        "schema": "d1_remote_tower_entity_resource_census/v1",
        "status": (
            "D1_TOWER_ENTITY_RESOURCE_CENSUS_COMPLETE"
            if not violations
            else "D1_TOWER_ENTITY_RESOURCE_CENSUS_PARTIAL"
        ),
        "source_map_data_layer": str(a.map_data_layer),
        "map_entry_entity_count": len(entity_hashes),
        "unique_entity_resource_hash_count": len(resource_hashes),
        "entity_class": ENTITY_CLASS,
        "entity_resource_class": ENTITY_RESOURCE_CLASS,
        "semantic_role_counts": dict(roles),
        "unk08_class_counts": dict(unk08),
        "unk10_class_counts": dict(unk10),
        "unk18_class_counts": dict(unk18),
        "unk10_class_candidates": candidate_classes,
        "global_channel_parent_class_source_lead": {
            "repository": "Rhys-Kovacevic/charm_exporter",
            "commit": "4bdce74798549f50d3687732d47ec5183a516069",
            "discriminator_struct": "S79948080",
            "d1_discriminator_class": D1_GLOBAL_CHANNEL_DISCRIMINATOR_CLASS,
            "parent_struct": "S79818080",
            "d1_parent_class": D1_GLOBAL_CHANNEL_PARENT_CLASS,
            "d1_program_entry_class": D1_GLOBAL_CHANNEL_ENTRY_CLASS,
            "d1_program_arrays": ["+0x110", "+0x120", "+0x130"],
            "d1_channel_id_array": "+0x140",
            "entry_channel_index": "+0x20",
            "entry_bytecode_array": "+0x28",
            "entry_vec4_constants_array": "+0x38",
            "source_export_behavior": "GlobalExporter accepts S79948080 discriminator, casts Unk18 to S79818080, and joins SD1918080.ChannelIndex through S79818080.Array3 IDs.",
        },
        "global_channel_parents": global_channel_parents,
        "requested_tower_light_channel_indices": [
            f"0x{x:02X}" for x in sorted(REQUESTED_LIGHT_CHANNELS)
        ],
        "entities": entities,
        "resources": resources,
        "packages": [
            corpus.package_rows[p] for p in sorted(corpus.package_rows)
        ],
        "violations": violations,
        "policy": (
            "Map ownership comes only from the supplied exact SMapDataTable census. "
            "Entity resources are read only through source-pinned D1 SEntity +0x20 "
            "DynamicArray framing and exact current logical package views. Every "
            "raw ResourcePointer class is preserved. No unknown discriminator is "
            "named from frequency, owner location, or later-engine class names."
        ),
    }

    a.out.parent.mkdir(parents=True, exist_ok=True)
    a.out.write_text(json.dumps(out, indent=2) + "\n")
    print(
        json.dumps(
            {
                "status": out["status"],
                "map_entry_entity_count": out["map_entry_entity_count"],
                "unique_entity_resource_hash_count": out[
                    "unique_entity_resource_hash_count"
                ],
                "semantic_role_counts": out["semantic_role_counts"],
                "unk10_class_counts": out["unk10_class_counts"],
                "global_channel_parent_count": len(global_channel_parents),
                "requested_global_channel_programs": [],
                "requested_global_channel_programs_note": (
                    "Requires exact StringHash join from local sequencer Array3 IDs "
                    "to ordered GlobalChannelDefaults; local ChannelIndex is not the "
                    "raw TFX 0x4B global index."
                ),
                "violations": violations[:20],
                "violation_count": len(violations),
            },
            indent=2,
        )
    )
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
