#!/usr/bin/env python3
"""Cross-source negative census for API10 in pinned Charm shader/exporter source.

This is tooling/source evidence, not retail runtime evidence. It establishes
that the pinned TfxScope declaration omits index 10 and that the explicit
CBuffer handling in Source2Handler covers 2, 8, and 13, not 10.
"""
import argparse,json,re
from pathlib import Path

EXPECTED_SCOPE={1:"Instance",2:"Transparent",3:"Unk3",8:"Unk8",9:"Decal",12:"View",13:"Frame"}
EXPECTED_EXPORTER={2,8,13}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument("--externs",type=Path,required=True)
    ap.add_argument("--source2",type=Path,required=True)
    ap.add_argument("-o","--out",type=Path,required=True)
    a=ap.parse_args(); violations=[]
    e=a.externs.read_text(encoding="utf-8-sig")
    m=re.search(r"public\s+enum\s+TfxScope\s*:\s*byte\s*\{(.*?)\}",e,re.S)
    scope={int(v):n for n,v in re.findall(r"^\s*([A-Za-z_]\w*)\s*=\s*(\d+)\s*,?",m.group(1),re.M)} if m else {}
    if scope!=EXPECTED_SCOPE: violations.append("tfxscope_mapping_drift")
    s=a.source2.read_text(encoding="utf-8-sig")
    block=re.search(r"foreach \(var resource in materialHeader\.PixelShader\.Resources\)(.*?)(?:vmat\.AppendLine\(\$?"\\t}}"\))",s,re.S)
    if not block: violations.append("pixel_resource_block_missing"); handled=set()
    else: handled={int(x) for x in re.findall(r"case\s+(\d+)\s*:",block.group(1))}
    if handled!=EXPECTED_EXPORTER: violations.append(f"explicit_cbuffer_handling_drift:{sorted(handled)}")
    if 10 in scope or 10 in handled: violations.append("api10_unexpected_source_handling")
    exact=not violations
    out={
      "schema":"d1_api10_charm_cross_source_negative_census/v1",
      "status":"D1_API10_CHARM_CROSS_SOURCE_NEGATIVE_EXACT" if exact else "D1_API10_CHARM_CROSS_SOURCE_NEGATIVE_VIOLATIONS",
      "tfxscope_mapping":{str(k):v for k,v in sorted(scope.items())},
      "source2_explicit_cbuffer_indices":sorted(handled),
      "api10":{"in_tfxscope":10 in scope,"explicitly_handled_by_source2":10 in handled,"runtime_writer":"WITHHELD","backing_allocation":"WITHHELD","engine_semantic":"WITHHELD"},
      "evidence_class":"PINNED_COMMUNITY_SOURCE_NOT_RETAIL_RUNTIME",
      "violations":violations,
      "policy":"This census only excludes deriving API10 semantics from these pinned source locations. It cannot establish retail runtime writer, allocation, or semantic."
    }
    a.out.parent.mkdir(parents=True,exist_ok=True); a.out.write_text(json.dumps(out,indent=2)+"\n")
    print(json.dumps(out,indent=2)); return 0 if exact else 2

if __name__=="__main__": raise SystemExit(main())
