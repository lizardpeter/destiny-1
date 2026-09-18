#!/usr/bin/env python3
"""Fail-closed audit for production D1 texture consumer paths.

The legacy d1_texture_export module retains low-level decoding and a permissive
follow_backing helper for historical/diagnostic compatibility. Production
entry points must not import its export_reader directly; they must route through
d1_texture_export_v2 or independently consume the shared
d1_texture_backing_chain_v1 resolver.

This is a source-policy regression, not retail semantic evidence.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

DEFAULT_PRODUCTION=[
 "tools/d1_texture_export_generation_safe.py",
 "tools/d1_texture_census_tolerant.py",
 "tools/d1_remote_texture_export.py",
 "tools/d1_remote_texture_export_generation_safe.py",
 "tools/d1_world_material_texture_export.py",
 "tools/d1_remote_activity_material_dependency_closure.py",
 "tools/d1_remote_activity_texture_export.py",
]

def audit(root:Path,paths:list[str])->dict:
 rows=[];viol=[]
 for rel in paths:
  p=root/rel
  if not p.is_file():
   viol.append(f"missing_production_consumer:{rel}");continue
  txt=p.read_text(errors="replace")
  direct=bool(re.search(r"from\s+d1_texture_export\s+import[^\n]*\bexport_reader\b",txt))
  via_v2=bool(re.search(r"from\s+d1_texture_export_v2\s+import[^\n]*\bexport_reader\b",txt))
  shared=bool(re.search(r"from\s+d1_texture_backing_chain_v1\s+import[^\n]*\bresolve_texture_backing\b",txt))
  low_level=bool(re.search(r"from\s+d1_texture_export\s+import",txt))
  if direct:
   viol.append(f"{rel}:direct_legacy_export_reader_import")
  if rel.endswith("d1_world_material_texture_export.py") and not shared:
   viol.append(f"{rel}:missing_shared_backing_resolver")
  if rel.endswith("d1_remote_activity_material_dependency_closure.py") and not shared:
   viol.append(f"{rel}:missing_shared_backing_resolver")
  if rel.endswith("d1_remote_texture_export_generation_safe.py") and not shared:
   viol.append(f"{rel}:missing_shared_backing_resolver")
  if rel in {
   "tools/d1_texture_export_generation_safe.py",
   "tools/d1_texture_census_tolerant.py",
   "tools/d1_remote_texture_export.py",
  } and not via_v2:
   viol.append(f"{rel}:not_routed_through_v2")
  rows.append({
   "path":rel,
   "imports_legacy_low_level":low_level,
   "imports_legacy_export_reader":direct,
   "routes_export_reader_via_v2":via_v2,
   "imports_shared_backing_resolver":shared,
  })
 return {
  "schema":"d1_texture_consumer_policy_audit/v1",
  "status":"D1_TEXTURE_CONSUMER_POLICY_EXACT" if not viol else "D1_TEXTURE_CONSUMER_POLICY_VIOLATIONS",
  "production_consumer_count":len(paths),
  "rows":rows,
  "violations":viol,
  "policy":"Production callers may reuse low-level decode/unswizzle helpers, but may not call the permissive legacy export_reader directly. Storage-shape decisions must route through v2 or the shared fail-closed backing resolver.",
 }

def main()->int:
 ap=argparse.ArgumentParser();ap.add_argument("--root",type=Path,default=Path(__file__).resolve().parents[1]);ap.add_argument("--path",action="append");ap.add_argument("-o","--output",type=Path)
 a=ap.parse_args();out=audit(a.root,a.path or DEFAULT_PRODUCTION)
 if a.output:
  a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+"\n")
 print(json.dumps(out,indent=2));return 0 if not out["violations"] else 2

if __name__=="__main__":raise SystemExit(main())
