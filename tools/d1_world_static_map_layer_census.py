#!/usr/bin/env python3
"""Census every D1 ROI SStaticMapData reached from a map-layer census.

This follows only already-serialized ownership edges:
  SMapDataEntry ResourcePointer -> SMapDataResource (80801AEA)
  +0x0C -> SStaticMapParent (80801AC6)
  parent +0x08 -> SStaticMapData (808008B4)

For each SStaticMapData it preserves the direct D1 baked-static child and the
embedded BA048080 decal/model records.  The embedded records are important: a D1
world contains far more than the minority SStaticMapData resources that have a
D1StaticMapData child at +0x30.

No visual or proximity inference is used.  Unknown/non-singleton records remain
in the report instead of being normalized away.
"""
from __future__ import annotations

import argparse, json, math, struct, sys
from collections import Counter, defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5

STATIC_MAP_PARENT='80801AC6'
STATIC_MAP_DATA='808008B4'
STATIC_MAP_D1='80801B75'
OCCLUSION_BOUNDS='80800583'
ENTITY_MODEL='80801AB5'


def norm(x): return str(x).upper().removeprefix('0X').zfill(8)
def hx(x): return f'{x:08X}'
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def u64(b,o): return struct.unpack_from('<Q',b,o)[0]
def f16(b,o): return [float(x) for x in struct.unpack_from('<16f',b,o)]
def f4(b,o): return [float(x) for x in struct.unpack_from('<4f',b,o)]


def meta(c,h,expected=None):
    h=norm(h); m=c.entry_meta(h)
    return {
        'hash':h,
        'exists':m is not None,
        'expected_reference':expected,
        'reference_matches':bool(m and (expected is None or norm(m.get('reference',''))==expected)),
        'meta':m,
    }


def parse_decal(c,b,ro,index):
    dyn=v5.v3.base.dyn
    row={'index':index,'record_offset':ro,'declared_size':u64(b,ro),'violations':[]}
    ta=dyn(b,ro+0x08,0x40); ua=dyn(b,ro+0x18,0x10); ma=dyn(b,ro+0x28,0x04)
    row['arrays']={'transforms':ta,'unk18':ua,'models':ma}
    for name,a in row['arrays'].items():
        if not a.get('ok'): row['violations'].append(f'{name} dynamic array bounds')
    row['transforms']=[]
    if ta.get('ok'):
        for i in range(ta['count']):
            o=ta['absolute']+i*0x40; vals=f16(b,o)
            finite=all(math.isfinite(x) for x in vals)
            if not finite: row['violations'].append(f'transform[{i}] non-finite')
            row['transforms'].append({'index':i,'offset':o,'finite':finite,
                                      'rows':[vals[j:j+4] for j in range(0,16,4)]})
    row['unk18_vectors']=[]
    if ua.get('ok'):
        for i in range(ua['count']):
            o=ua['absolute']+i*0x10; vals=f4(b,o); finite=all(math.isfinite(x) for x in vals)
            if not finite: row['violations'].append(f'unk18[{i}] non-finite')
            row['unk18_vectors'].append({'index':i,'offset':o,'finite':finite,'value':vals})
    row['models']=[]
    if ma.get('ok'):
        for i in range(ma['count']):
            o=ma['absolute']+i*4; h=hx(u32(b,o)); tm=meta(c,h,ENTITY_MODEL)
            row['models'].append({'index':i,'offset':o,**tm})
            if not tm['reference_matches']:
                row['violations'].append(f'model[{i}] {h} missing/class mismatch')
    row['singleton_transform_model']=bool(ta.get('ok') and ma.get('ok') and ta['count']==1 and ma['count']==1)
    row['ok']=not row['violations']
    return row


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--snapshot',type=Path,action='append',required=True)
    ap.add_argument('--runtime',type=Path,required=True)
    ap.add_argument('--map-layer-census',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    src=json.loads(a.map_layer_census.read_text())
    c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    source_rows=[r for t in src.get('tables',[]) for r in t.get('entries',[])]
    rows=[]; violations=[]
    for sr in source_rows:
        pr=(sr.get('resource_target') or {}).get('hash')
        row={
            'map_data_table':sr.get('map_data_table'),'map_entry_index':sr.get('index'),
            'outer_rotation':sr.get('rotation'),'outer_translation':sr.get('translation'),
            'world_id':sr.get('world_id'),'static_map_parent':pr,'violations':[],'decals':[]
        }
        if not pr:
            row['violations'].append('map row lacks static-map parent target'); rows.append(row); continue
        pm=meta(c,pr,STATIC_MAP_PARENT); row['static_map_parent_meta']=pm
        if not pm['reference_matches']:
            row['violations'].append('static-map parent missing/class mismatch'); rows.append(row); continue
        pb,psrc=c.payload(pr); row['static_map_parent_source']=psrc
        if pb is None or len(pb)<0x0C:
            row['violations'].append('static-map parent payload unavailable/short'); rows.append(row); continue
        sm=hx(u32(pb,0x08)); row['static_map']=sm; smm=meta(c,sm,STATIC_MAP_DATA); row['static_map_meta']=smm
        if not smm['reference_matches']:
            row['violations'].append('SStaticMapData missing/class mismatch'); rows.append(row); continue
        b,bsrc=c.payload(sm); row['static_map_source']=bsrc
        if b is None or len(b)<0x38:
            row['violations'].append('SStaticMapData payload unavailable/short'); rows.append(row); continue
        row['static_map_payload_bytes']=len(b)
        da=v5.v3.base.dyn(b,0x08,0x80); row['decals_array']=da
        if not da.get('ok'):
            row['violations'].append('embedded decal array bounds')
        occ=hx(u32(b,0x18)); row['occlusion_bounds']=meta(c,occ,OCCLUSION_BOUNDS)
        d1=hx(u32(b,0x30)); row['d1_static_child_raw']=d1
        row['has_direct_d1_static_child']=d1 not in ('00000000','FFFFFFFF')
        row['d1_static_child']=meta(c,d1,STATIC_MAP_D1) if row['has_direct_d1_static_child'] else None
        if row['has_direct_d1_static_child'] and not row['d1_static_child']['reference_matches']:
            row['violations'].append('D1 static child missing/class mismatch')
        if da.get('ok'):
            for i in range(da['count']):
                row['decals'].append(parse_decal(c,b,da['absolute']+i*0x80,i))
            if any(not x['ok'] for x in row['decals']): row['violations'].append('one or more embedded records invalid')
        row['embedded_decal_count']=da.get('count') if da.get('ok') else None
        row['embedded_model_reference_occurrences']=sum(len(x.get('models',[])) for x in row['decals'])
        row['ok']=not row['violations']
        rows.append(row)

    sm_hist=Counter(r.get('static_map') or 'NULL' for r in rows)
    parent_hist=Counter(r.get('static_map_parent') or 'NULL' for r in rows)
    model_hist=Counter(m['hash'] for r in rows for d in r.get('decals',[]) for m in d.get('models',[]) if m.get('reference_matches'))
    d1rows=[r for r in rows if r.get('has_direct_d1_static_child')]
    embrows=[r for r in rows if (r.get('embedded_decal_count') or 0)>0]
    decals=[d for r in rows for d in r.get('decals',[])]
    allviol=[{'map_data_table':r.get('map_data_table'),'map_entry_index':r.get('map_entry_index'),'static_map_parent':r.get('static_map_parent'),'static_map':r.get('static_map'),'violations':r.get('violations')} for r in rows if r.get('violations')]
    out={
        'schema_version':1,
        'status':'D1_WORLD_STATIC_MAP_LAYER_CENSUS' if not allviol else 'D1_WORLD_STATIC_MAP_LAYER_CENSUS_PARTIAL',
        'source_map_layer_census':str(a.map_layer_census),
        'source_map_entry_count':len(source_rows),
        'unique_static_map_parents':len([x for x in parent_hist if x!='NULL']),
        'unique_static_maps':len([x for x in sm_hist if x!='NULL']),
        'direct_d1_static_child_rows':len(d1rows),
        'embedded_record_static_map_rows':len(embrows),
        'embedded_record_count':len(decals),
        'singleton_transform_model_records':sum(bool(x.get('singleton_transform_model')) for x in decals),
        'embedded_model_reference_occurrences':sum(model_hist.values()),
        'unique_embedded_entity_models':len(model_hist),
        'embedded_entity_model_histogram':dict(model_hist),
        'static_map_histogram':dict(sm_hist),'static_map_parent_histogram':dict(parent_hist),
        'rows':rows,'violations':allviol,
        'policy':'Only serialized SMapDataEntry -> 80801AEA -> 80801AC6 -> 808008B4 ownership is followed. Embedded BA048080 arrays are preserved exactly; no scene-membership guess is made.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','source_map_entry_count','unique_static_map_parents','unique_static_maps','direct_d1_static_child_rows','embedded_record_static_map_rows','embedded_record_count','singleton_transform_model_records','embedded_model_reference_occurrences','unique_embedded_entity_models')},indent=2))
    return 0 if not allviol else 2

if __name__=='__main__': raise SystemExit(main())
