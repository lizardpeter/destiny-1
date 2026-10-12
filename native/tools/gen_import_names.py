#!/usr/bin/env python3
"""Write import_names.inc ({"NID", "name"}, ...) from evidence/generated/d1_import_surface.json."""
import json
import sys

src, out = sys.argv[1], sys.argv[2]
rows = {}
for r in json.load(open(src))["imports"]:
    if r.get("name"):
        rows[r["nid"]] = r["name"]
with open(out, "w") as f:
    for nid, name in sorted(rows.items()):
        f.write('{"%s", "%s"},\n' % (nid, name.replace("\\", "\\\\").replace('"', '\\"')))
