#!/usr/bin/env python3
"""Recover exact D1 player-preview provenance from Bungie's published web assets.

This tool deliberately does not infer visible geometry or rig ownership.  It reads
Bungie's D1 manifest, the exact web player skeleton/animation JSON files, and the
mobile GearAsset SQLite databases used by the archived Spasm/TGX player preview.
For caller-supplied inventory hashes it reports only exact database/API matches.

The archived Bungie player viewer names these files directly:
  common/destiny_content/animations/destiny_player_skeleton.js
  common/destiny_content/animations/destiny_player_animation.js

The armory viewer also passes `gearAndDefaultArmor` to ItemPreview.  Recovering the
GearAsset rows is therefore the correct route to body-complete character assembly;
manual mesh-range restoration is intentionally outside this tool.
"""
from __future__ import annotations

import argparse
import hashlib
import io
import json
import re
import sqlite3
import struct
import urllib.error
import urllib.parse
import urllib.request
import zipfile
from pathlib import Path
from typing import Any

BUNGIE = "https://www.bungie.net"
DEFAULT_MANIFEST = BUNGIE + "/d1/Platform/Destiny/Manifest/"
DEFAULT_SKELETON = BUNGIE + "/common/destiny_content/animations/destiny_player_skeleton.js"
DEFAULT_ANIMATION = BUNGIE + "/common/destiny_content/animations/destiny_player_animation.js"


def norm_hash(text: str) -> tuple[int, int, str]:
    t = text.strip()
    if t.lower().startswith("0x") or re.fullmatch(r"[0-9a-fA-F]{8}", t):
        u = int(t.removeprefix("0x").removeprefix("0X"), 16) & 0xFFFFFFFF
    else:
        u = int(t, 10) & 0xFFFFFFFF
    s = u if u < 0x80000000 else u - 0x100000000
    return u, s, f"{u:08X}"


def fetch(url: str) -> bytes:
    req = urllib.request.Request(url, headers={
        "User-Agent": "Destiny1Reversal/1.0 exact-provenance-probe",
        "Accept": "*/*",
    })
    with urllib.request.urlopen(req, timeout=90) as r:
        return r.read()


def fetch_json(url: str) -> Any:
    raw = fetch(url)
    # Bungie's *.js animation resources are JSON payloads despite the suffix.
    return json.loads(raw.decode("utf-8-sig"))


def sha256(data: bytes) -> str:
    return hashlib.sha256(data).hexdigest()


def json_safe(v: Any) -> Any:
    if isinstance(v, bytes):
        out = {"byte_length": len(v), "sha256": sha256(v)}
        try:
            text = v.decode("utf-8-sig")
        except UnicodeDecodeError:
            return {"__blob__": out}
        out["utf8"] = text
        try:
            out["json"] = json.loads(text)
        except Exception:
            pass
        return {"__blob__": out}
    return v


def summarize_skeleton(obj: Any) -> dict[str, Any]:
    d = obj.get("definition", obj) if isinstance(obj, dict) else {}
    nodes = d.get("nodes", []) if isinstance(d, dict) else []
    hashes: list[str | None] = []
    parents: list[int | None] = []
    names: list[str | None] = []
    for n in nodes:
        h = None
        name = None
        if isinstance(n, dict):
            nm = n.get("name")
            if isinstance(nm, dict):
                if "hash" in nm:
                    try: h = f"{int(nm['hash']) & 0xFFFFFFFF:08X}"
                    except Exception: pass
                if "string" in nm: name = str(nm["string"])
            elif isinstance(nm, str):
                name = nm
            if h is None:
                for key in ("bone_hash", "hash"):
                    if key in n:
                        try: h = f"{int(n[key]) & 0xFFFFFFFF:08X}"
                        except Exception: pass
                        break
            p = n.get("parent_node_index", n.get("parentNodeIndex", n.get("parent")))
            try: p = int(p) if p is not None else None
            except Exception: p = None
        else:
            p = None
        hashes.append(h); parents.append(p); names.append(name)
    return {
        "root_keys": sorted(obj.keys()) if isinstance(obj, dict) else [],
        "definition_keys": sorted(d.keys()) if isinstance(d, dict) else [],
        "node_count": len(nodes),
        "node_hashes": hashes,
        "parent_node_indices": parents,
        "node_names": names,
        "default_object_space_transform_count": len(d.get("default_object_space_transforms", [])) if isinstance(d, dict) else 0,
        "default_inverse_object_space_transform_count": len(d.get("default_inverse_object_space_transforms", [])) if isinstance(d, dict) else 0,
    }


def summarize_json_shape(obj: Any, depth: int = 0) -> Any:
    if depth >= 3:
        if isinstance(obj, list): return {"type": "list", "count": len(obj)}
        if isinstance(obj, dict): return {"type": "dict", "keys": sorted(obj.keys())[:80]}
        return {"type": type(obj).__name__}
    if isinstance(obj, dict):
        return {k: summarize_json_shape(v, depth + 1) for k, v in list(obj.items())[:100]}
    if isinstance(obj, list):
        return {
            "type": "list", "count": len(obj),
            "first": summarize_json_shape(obj[0], depth + 1) if obj else None,
        }
    return {"type": type(obj).__name__, "value": obj if isinstance(obj, (str, int, float, bool)) else None}


def materialize_sqlite(raw: bytes, dest: Path) -> tuple[Path, dict[str, Any]]:
    meta: dict[str, Any] = {"download_bytes": len(raw), "download_sha256": sha256(raw)}
    bio = io.BytesIO(raw)
    if zipfile.is_zipfile(bio):
        with zipfile.ZipFile(io.BytesIO(raw)) as z:
            names = [n for n in z.namelist() if not n.endswith("/")]
            if not names:
                raise ValueError("GearAsset archive has no files")
            # Prefer the first SQLite-looking member, otherwise the largest member.
            candidates = sorted(names, key=lambda n: (not (n.endswith(".content") or n.endswith(".sqlite") or n.endswith(".db")), -z.getinfo(n).file_size))
            name = candidates[0]
            payload = z.read(name)
            meta.update({"container": "zip", "zip_member": name, "sqlite_bytes": len(payload), "sqlite_sha256": sha256(payload)})
    else:
        payload = raw
        meta.update({"container": "raw", "sqlite_bytes": len(payload), "sqlite_sha256": sha256(payload)})
    dest.write_bytes(payload)
    return dest, meta


def table_columns(con: sqlite3.Connection, table: str) -> list[dict[str, Any]]:
    q = 'PRAGMA table_info("' + table.replace('"', '""') + '")'
    return [
        {"cid": r[0], "name": r[1], "type": r[2], "notnull": bool(r[3]), "default": r[4], "pk": r[5]}
        for r in con.execute(q)
    ]


def search_database(db: Path, wanted: list[tuple[int, int, str]]) -> dict[str, Any]:
    con = sqlite3.connect(str(db))
    con.row_factory = sqlite3.Row
    tables = [r[0] for r in con.execute("SELECT name FROM sqlite_master WHERE type='table' ORDER BY name")]
    schema = []
    hits: list[dict[str, Any]] = []
    try:
        for table in tables:
            cols = table_columns(con, table)
            schema.append({"table": table, "columns": cols})
            int_cols = [c["name"] for c in cols if any(x in (c["type"] or "").upper() for x in ("INT", "NUM")) or c["name"].lower() in {"id", "hash", "itemhash", "item_hash", "referenceid", "reference_id"}]
            text_cols = [c["name"] for c in cols if any(x in (c["type"] or "").upper() for x in ("TEXT", "CHAR", "CLOB"))]
            qtable = '"' + table.replace('"', '""') + '"'
            for u, s, hx in wanted:
                seen_rowids: set[int] = set()
                for col in int_cols:
                    qcol = '"' + col.replace('"', '""') + '"'
                    sql = f"SELECT rowid AS __rowid__, * FROM {qtable} WHERE {qcol}=? OR {qcol}=? LIMIT 32"
                    try: rows = con.execute(sql, (u, s)).fetchall()
                    except sqlite3.Error: continue
                    for row in rows:
                        rid = int(row["__rowid__"])
                        if rid in seen_rowids: continue
                        seen_rowids.add(rid)
                        hits.append({
                            "target_hash": hx, "target_uint32": u, "target_int32": s,
                            "table": table, "match_column": col, "match_kind": "integer_exact",
                            "rowid": rid, "row": {k: json_safe(row[k]) for k in row.keys() if k != "__rowid__"},
                        })
                # Text fallback is still exact-token based, not semantic guessing.
                tokens = (str(u), str(s), hx, hx.lower(), "0x" + hx, "0x" + hx.lower())
                for col in text_cols:
                    qcol = '"' + col.replace('"', '""') + '"'
                    ors = " OR ".join([f"instr({qcol}, ?) > 0" for _ in tokens])
                    sql = f"SELECT rowid AS __rowid__, * FROM {qtable} WHERE {ors} LIMIT 32"
                    try: rows = con.execute(sql, tokens).fetchall()
                    except sqlite3.Error: continue
                    for row in rows:
                        rid = int(row["__rowid__"])
                        if rid in seen_rowids: continue
                        seen_rowids.add(rid)
                        hits.append({
                            "target_hash": hx, "target_uint32": u, "target_int32": s,
                            "table": table, "match_column": col, "match_kind": "text_exact_token",
                            "rowid": rid, "row": {k: json_safe(row[k]) for k in row.keys() if k != "__rowid__"},
                        })
    finally:
        con.close()
    return {"tables": schema, "hits": hits, "hit_count": len(hits)}


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--manifest-url", default=DEFAULT_MANIFEST)
    ap.add_argument("--skeleton-url", default=DEFAULT_SKELETON)
    ap.add_argument("--animation-url", default=DEFAULT_ANIMATION)
    ap.add_argument("--inventory-hash", action="append", required=True)
    ap.add_argument("--download-dir", type=Path, required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    a.download_dir.mkdir(parents=True, exist_ok=True)
    wanted = [norm_hash(x) for x in a.inventory_hash]

    manifest_raw = fetch(a.manifest_url)
    manifest_obj = json.loads(manifest_raw.decode("utf-8-sig"))
    manifest = manifest_obj.get("Response", manifest_obj)
    (a.download_dir / "d1_manifest.json").write_bytes(manifest_raw)

    skeleton_raw = fetch(a.skeleton_url)
    skeleton_obj = json.loads(skeleton_raw.decode("utf-8-sig"))
    (a.download_dir / "destiny_player_skeleton.js").write_bytes(skeleton_raw)

    animation_raw = fetch(a.animation_url)
    animation_obj = json.loads(animation_raw.decode("utf-8-sig"))
    (a.download_dir / "destiny_player_animation.js").write_bytes(animation_raw)

    single_defs = []
    for u, s, hx in wanted:
        url = f"{BUNGIE}/d1/Platform/Destiny/Manifest/InventoryItem/{u}/"
        try:
            raw = fetch(url)
            obj = json.loads(raw.decode("utf-8-sig"))
            path = a.download_dir / f"inventory_{hx}.json"
            path.write_bytes(raw)
            single_defs.append({"hash": hx, "uint32": u, "int32": s, "url": url, "sha256": sha256(raw), "response": obj})
        except Exception as ex:
            single_defs.append({"hash": hx, "uint32": u, "int32": s, "url": url, "error": repr(ex)})

    db_reports = []
    for i, desc in enumerate(manifest.get("mobileGearAssetDataBases", []) or []):
        rel = desc.get("path")
        if not rel: continue
        url = urllib.parse.urljoin(BUNGIE + "/", rel.lstrip("/"))
        try:
            raw = fetch(url)
            db_path = a.download_dir / f"gear_asset_{i}.sqlite"
            _, mat_meta = materialize_sqlite(raw, db_path)
            scan = search_database(db_path, wanted)
            db_reports.append({"index": i, "manifest_descriptor": desc, "url": url, **mat_meta, **scan})
        except Exception as ex:
            db_reports.append({"index": i, "manifest_descriptor": desc, "url": url, "error": repr(ex)})

    rep = {
        "schema": "d1_bungie_player_preview_probe/v1",
        "policy": "Exact published Bungie D1 web-preview provenance only. No mesh range, body item, skeleton, rig, or animation ownership is inferred from compatibility.",
        "manifest": {
            "url": a.manifest_url, "sha256": sha256(manifest_raw), "version": manifest.get("version"),
            "mobileGearAssetDataBases": manifest.get("mobileGearAssetDataBases"),
            "mobileGearCDN": manifest.get("mobileGearCDN"),
            "mobileAssetContentPath": manifest.get("mobileAssetContentPath"),
        },
        "player_skeleton": {
            "url": a.skeleton_url, "bytes": len(skeleton_raw), "sha256": sha256(skeleton_raw),
            "summary": summarize_skeleton(skeleton_obj),
        },
        "player_animation": {
            "url": a.animation_url, "bytes": len(animation_raw), "sha256": sha256(animation_raw),
            "shape": summarize_json_shape(animation_obj),
        },
        "inventory_targets": [{"hash": hx, "uint32": u, "int32": s} for u, s, hx in wanted],
        "single_definitions": single_defs,
        "gear_asset_databases": db_reports,
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(rep, indent=2) + "\n")

    sk = rep["player_skeleton"]["summary"]
    print("MANIFEST", rep["manifest"]["version"])
    print("PLAYER SKELETON", sk["node_count"], "nodes", rep["player_skeleton"]["sha256"])
    print("PLAYER ANIMATION bytes", rep["player_animation"]["bytes"], rep["player_animation"]["sha256"])
    for db in db_reports:
        print("GEAR DB", db["index"], "hits", db.get("hit_count"), "error", db.get("error"))
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
