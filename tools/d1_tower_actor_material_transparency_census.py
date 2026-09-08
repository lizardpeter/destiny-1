#!/usr/bin/env python3
"""Census exact D1 transparency/blend-selector state for active Tower actor materials.

Source-backed facts used here:
- D1 Material class is 80801AD7.
- Charm's D1 map-decal/transparent selection treats material.Unk20 != 0 as
  transparent draw population.
- material +0x20 low byte 0x88 is independently closed to blend-state index 8,
  Source + Destination*(1-SourceAlpha).

Other nonzero +0x20 encodings are retained but their exact blend equations are not
invented.  For portable glTF, they can safely be classified as BLEND candidates,
not as exact native blend equations.
"""
from __future__ import annotations

import argparse, hashlib, json, struct, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))
import d1_tower_map_schema_validate_v5 as v5

MATERIAL_CLASS = '80801AD7'
NULLS = {'00000000','FFFFFFFF'}


def norm(x): return str(x).upper().removeprefix('0X').zfill(8)
def u16(b,o): return struct.unpack_from('<H', b, o)[0]
def u32(b,o): return struct.unpack_from('<I', b, o)[0]
def hbytes(b): return hashlib.sha256(b).hexdigest()


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument('--snapshot', type=Path, action='append', required=True)
    ap.add_argument('--runtime', type=Path, required=True)
    ap.add_argument('--visual-json', type=Path, required=True)
    ap.add_argument('-o','--out', type=Path, required=True)
    a = ap.parse_args()

    src = json.loads(a.visual_json.read_text())
    materials = sorted(norm(x) for x in (src.get('materials') or {}).keys())
    if not materials:
        raise SystemExit('visual selector contains no materials')
    c = v5.v3.base.Corpus([p.resolve() for p in a.snapshot], a.runtime.resolve())
    rows=[]; violations=[]
    raw16_counts=Counter(); low_counts=Counter(); ps_by_trans=defaultdict(Counter)
    for h in materials:
        meta=c.entry_meta(h); b,source=c.payload(h)
        if meta is None or b is None:
            violations.append(f'{h}: material payload unavailable'); continue
        ref=norm(meta.get('reference',''))
        if ref != MATERIAL_CLASS:
            violations.append(f'{h}: class {ref} != {MATERIAL_CLASS}'); continue
        if len(b) < 0x2AC:
            violations.append(f'{h}: payload too short {len(b)}'); continue
        raw16=u16(b,0x20); lo=int(b[0x20]); hi=int(b[0x21]); vs=norm(u32(b,0x28)); ps=norm(u32(b,0x2A8))
        transparent=raw16 != 0
        raw16_counts[f'0x{raw16:04X}'] += 1; low_counts[f'0x{lo:02X}'] += 1; ps_by_trans['transparent' if transparent else 'opaque'][ps]+=1
        known = lo == 0x88
        rows.append({
            'material':h,'source':source,'payload_sha256':hbytes(b),'payload_bytes':len(b),
            'unk20_raw_u16':raw16,'unk20_hex':f'0x{raw16:04X}','unk20_low_u8':lo,'unk20_low_hex':f'0x{lo:02X}','unk20_high_u8':hi,
            'transparent_draw_population':transparent,'vertex_shader':vs,'pixel_shader':ps,
            'portable_alpha_mode':'BLEND' if transparent else 'OPAQUE',
            'exact_blend_state_known':known,
            'exact_blend_state_index':8 if known else None,
            'exact_blend_equation':'Source + Destination*(1-SourceAlpha)' if known else None,
        })
    if len(rows) != len(materials): violations.append(f'resolved {len(rows)} of {len(materials)} materials')
    out={
        'schema_version':1,
        'status':'D1_TOWER_ACTOR_MATERIAL_TRANSPARENCY_CENSUS_COMPLETE' if not violations else 'D1_TOWER_ACTOR_MATERIAL_TRANSPARENCY_CENSUS_PARTIAL',
        'material_count':len(materials),'resolved_material_count':len(rows),
        'transparent_material_count':sum(x['transparent_draw_population'] for x in rows),
        'opaque_material_count':sum(not x['transparent_draw_population'] for x in rows),
        'known_0x88_blend_material_count':sum(x['exact_blend_state_known'] for x in rows),
        'unk20_raw_counts':dict(sorted(raw16_counts.items())),
        'unk20_low_byte_counts':dict(sorted(low_counts.items())),
        'transparent_pixel_shader_counts':dict(sorted(ps_by_trans['transparent'].items())),
        'opaque_pixel_shader_counts':dict(sorted(ps_by_trans['opaque'].items())),
        'materials':rows,'violations':violations,
        'proof':{
            'D1_Unk20_nonzero_transparent_population_source_closed':True,
            'blend_selector_0x88_state8_equation_source_closed':True,
            'other_nonzero_blend_equations_source_closed':False,
        },
        'policy':'Portable alphaMode uses BLEND for the source-backed D1 transparent population and OPAQUE for Unk20==0. Only low byte 0x88 carries an exact native blend-equation claim.'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','material_count','transparent_material_count','opaque_material_count','known_0x88_blend_material_count','unk20_raw_counts','violations')},indent=2))
    return 0 if not violations else 2

if __name__=='__main__': raise SystemExit(main())
