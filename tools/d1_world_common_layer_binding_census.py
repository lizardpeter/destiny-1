#!/usr/bin/env python3
"""Prove the serialized binding between D1 map rows and common-layer records.

Tower's D1 SStaticMapParent resources carry a small integer at +0x10.  Across all
nine Tower common-layer groups this field is a zero-based permutation of the
embedded D1Class_BA048080 record indices.  This tool validates that invariant
against shipped package bytes and emits the selected record beside every map row.

Important: some final inline SMapDataResource pointer locations sit exactly past
the resident map-table payload even though the referenced SStaticMapParent itself
is valid and complete.  The selector is in SStaticMapParent, so lack of those
inline bytes is preserved as provenance and is not allowed to drop a valid row.
"""
from __future__ import annotations
import argparse,json,struct,sys
from collections import defaultdict
from pathlib import Path

HERE=Path(__file__).resolve().parent
sys.path.insert(0,str(HERE))
import d1_tower_map_schema_validate_v5 as v5

STATIC_MAP_PARENT='80801AC6'; STATIC_MAP_DATA='808008B4'
NULLS={'00000000','FFFFFFFF'}

def norm(x): return str(x).upper().removeprefix('0X').zfill(8)
def u16(b,o): return struct.unpack_from('<H',b,o)[0]
def u32(b,o): return struct.unpack_from('<I',b,o)[0]
def hx(x): return f'{x:08X}'
def words(b,o,n): return [u32(b,o+4*i) for i in range(n)]
def f16(b,o): return [float(x) for x in struct.unpack_from('<16f',b,o)]

def parse_common_records(sm,b):
    a=v5.v3.base.dyn(b,0x08,0x80)
    if not a.get('ok'): raise ValueError(f'{sm}: common embedded array invalid: {a}')
    out=[]
    for i in range(a['count']):
        ro=a['absolute']+i*0x80
        ta=v5.v3.base.dyn(b,ro+0x08,0x40); ma=v5.v3.base.dyn(b,ro+0x28,0x04)
        if not ta.get('ok') or not ma.get('ok') or ta['count']!=1 or ma['count']!=1:
            raise ValueError(f'{sm}: record {i} not singleton transform/model')
        mh=hx(u32(b,ma['absolute'])); tr=f16(b,ta['absolute'])
        out.append({'record_index':i,'record_offset':ro,'model':mh,'transform_rows':[tr[j:j+4] for j in range(0,16,4)]})
    return out

def exact_sequence(values,n,base=0): return values==list(range(base,base+n))
def permutation_sequence(values,n,base=0): return sorted(values)==list(range(base,base+n))

def field_tests(rows,n):
    tests=[]
    names=[]
    if rows:
        names=[k for k,v in rows[0].items() if isinstance(v,int) and (k.startswith('resource_u32_') or k.startswith('parent_u32_') or k.startswith('resource_u16_') or k.startswith('parent_u16_'))]
    for name in names:
        if not all(name in r and isinstance(r[name],int) for r in rows):
            continue
        vals=[int(r[name]) for r in rows]
        for mask,label in [(0xffffffff,'u32'),(0xffff,'low16'),(0xff,'low8')]:
            mv=[v&mask for v in vals]
            if exact_sequence(mv,n,0) or exact_sequence(mv,n,1) or permutation_sequence(mv,n,0) or permutation_sequence(mv,n,1):
                tests.append({'field':name,'view':label,'values':mv,
                              'exact_zero_based':exact_sequence(mv,n,0),'exact_one_based':exact_sequence(mv,n,1),
                              'permutation_zero_based':permutation_sequence(mv,n,0),'permutation_one_based':permutation_sequence(mv,n,1)})
    return tests

def main()->int:
    ap=argparse.ArgumentParser();ap.add_argument('--snapshot',type=Path,action='append',required=True);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--map-layer-census',type=Path,required=True);ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args();src=json.loads(a.map_layer_census.read_text());c=v5.v3.base.Corpus([p.resolve() for p in a.snapshot],a.runtime.resolve())
    groups=[];viol=[];inline_missing=[]
    for tab in src.get('tables',[]):
        th=norm(tab['map_data_table']);tb,tsrc=c.payload(th)
        if tb is None: viol.append(f'{th}: table payload unavailable');continue
        by_sm=defaultdict(list)
        for sr in tab.get('entries',[]):
            if norm(sr.get('resource_class') or '')!='80801AEA': continue
            parent=norm(((sr.get('resource_target') or {}).get('hash')) or 'FFFFFFFF')
            if parent in NULLS: continue
            pb,psrc=c.payload(parent);pm=c.entry_meta(parent)
            if pb is None or not pm or norm(pm.get('reference',''))!=STATIC_MAP_PARENT or len(pb)<0x28:
                viol.append(f'{th}:{sr.get("index")}: parent {parent} unavailable/class/short');continue
            sm=hx(u32(pb,0x08));smb,smsrc=c.payload(sm);smm=c.entry_meta(sm)
            if smb is None or not smm or norm(smm.get('reference',''))!=STATIC_MAP_DATA or len(smb)<0x38:
                viol.append(f'{th}:{sr.get("index")}: static map {sm} unavailable/class/short');continue
            d1=hx(u32(smb,0x30));has_d1=d1 not in NULLS
            if has_d1: continue

            # Parent bytes are authoritative for the record selector.  Preserve
            # inline SMapDataResource bytes when resident, but do not drop rows
            # solely because that inline pointer lands outside the resident table.
            ra=int(sr['resource_absolute'])
            row={'map_entry_index':int(sr['index']),'map_entry_record_offset':int(sr['record_offset']),'resource_absolute':ra,
                 'static_map_parent':parent,'static_map':sm,'parent_words_hex':[f'{x:08X}' for x in words(pb,0,10)]}
            pw=words(pb,0,10)
            for i,x in enumerate(pw): row[f'parent_u32_{i:02X}']=x
            for i in range(0,0x28,2): row[f'parent_u16_{i:02X}']=u16(pb,i)

            if 0 <= ra and ra+0x14 <= len(tb):
                rw=words(tb,ra,5);row['inline_resource_available']=True;row['resource_words_hex']=[f'{x:08X}' for x in rw]
                for i,x in enumerate(rw): row[f'resource_u32_{i:02X}']=x
                for i in range(0,0x14,2): row[f'resource_u16_{i:02X}']=u16(tb,ra+i)
            else:
                row['inline_resource_available']=False
                inline_missing.append({'map_data_table':th,'map_entry_index':int(sr['index']),'static_map_parent':parent,'static_map':sm,'resource_absolute':ra,'table_payload_size':len(tb)})
            by_sm[sm].append((row,smb,smsrc))

        for sm,items in by_sm.items():
            rows=[x[0] for x in items];records=parse_common_records(sm,items[0][1]);n=len(rows);nr=len(records)
            tests=field_tests(rows,n)
            # Shipped Tower evidence: SStaticMapParent +0x10 as a 32-bit value is
            # a complete zero-based permutation of the embedded record ordinals.
            selector_field='parent_u32_04'
            selector=[int(r[selector_field]) for r in rows]
            selector_ok=(n==nr and permutation_sequence(selector,n,0))
            if selector_ok:
                for ordinal,r in enumerate(rows):
                    idx=int(r[selector_field]);r['common_row_ordinal']=ordinal;r['selected_record_index']=idx;r['selected_record']=records[idx]
            else:
                viol.append(f'{th}:{sm}: +0x10 selector closure failed rows={n} records={nr} values={selector}')
            g={'map_data_table':th,'static_map':sm,'map_row_count':n,'embedded_record_count':nr,
               'count_matches':n==nr,'selector_field':selector_field,'selector_byte_offset':'0x10','selector_width_bits':32,
               'selector_zero_based_permutation':selector_ok,'field_sequence_tests':tests,'rows':rows,'records':records}
            groups.append(g)

    selected=sum(len(g['rows']) for g in groups if g['selector_zero_based_permutation'])
    out={'schema_version':2,'status':'D1_COMMON_LAYER_BINDING_PROVEN' if not viol else 'D1_COMMON_LAYER_BINDING_PARTIAL',
         'group_count':len(groups),'selected_record_placements':selected,'inline_resource_unavailable_rows':len(inline_missing),
         'inline_resource_unavailable':inline_missing,'groups':groups,'violations':viol,
         'proven_binding':{
             'container':'SStaticMapParent','field_offset':'0x10','interpretation':'zero-based embedded D1Class_BA048080 record selector',
             'tower_scope':'all nine common-layer groups','closure_requirement':'row count == embedded record count and selector values are an exact permutation of 0..N-1'
         },
         'policy':'The binding is promoted only because the same +0x10 parent field closes bijectively over every embedded record in all nine Tower groups. Missing inline SMapDataResource bytes are retained as provenance but cannot invalidate a complete parent-record selector.'}
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'group_count':len(groups),'selected_record_placements':selected,
                      'inline_resource_unavailable_rows':len(inline_missing),
                      'groups':[{'table':g['map_data_table'],'static_map':g['static_map'],'rows':g['map_row_count'],'records':g['embedded_record_count'],'selector_ok':g['selector_zero_based_permutation']} for g in groups],
                      'violations':viol},indent=2))
    return 0 if not viol else 2
if __name__=='__main__': raise SystemExit(main())
