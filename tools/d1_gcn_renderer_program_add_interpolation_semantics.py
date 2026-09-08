#!/usr/bin/env python3
"""Promote source-proven 808EE505 interpolation inputs in a D1 GCN renderer program.

Promotion is deliberately narrow. A V_INTERP_P1/P2 pair is promoted only when the
structural IR proves an exact matching destination+attribute pair, the IJ operands are
the expected v0/v1 pixel inputs, the attribute is already in the shader's exact input
set, and the renderer carries the pinned source-derived GCN interpolation equations.
"""
from __future__ import annotations
import argparse, collections, copy, json, re
from pathlib import Path

P1_EQ='D = P10(attribute) * IJ + P0(attribute)'
P2_EQ='D_new = P20(attribute) * IJ + D_old'
SOURCE_REV='f5c5a6e390f55dd5984977815bf9d0bd05da6945'
SOURCE_SHA='ce2b71f73f6883478c0d05335b57275153999cef76b7b549a2d15eb76bee472e'
RX=re.compile(r'^v_interp_p([12])_f32\s+(v\d+),\s+(v\d+),\s+(attr\d+\.[xyzw])$')


def contiguous(values):
    v=sorted(set(values)); out=[]
    if not v:return out
    a=b=v[0]
    for x in v[1:]:
        if x==b+1:b=x
        else:out.append((a,b));a=b=x
    out.append((a,b));return out


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--program',type=Path,required=True)
    ap.add_argument('--ir',type=Path,required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args(); violations=[]; result={}
    try:
        base=json.load(open(a.program)); ir=json.load(open(a.ir))
        assert base['status']=='D1_GCN_RENDERER_PROGRAM_IR_EXACT_PARTIAL' and not base['violations']
        p=base['program']; c=p['coverage']
        assert p['material']=='80D777B6' and p['pixel_shader']=='808EE505' and p['instruction_count']==456
        assert c['primary_resolution_counts']=={'CONTROL_EXACT':18,'EXPRESSION_EXACT':161,'INPUT_PROVENANCE_EXACT':30,'RECURRENCE_EXACT':36,'STRUCTURAL_ONLY':211},c
        assert c['exact_nonstructural_instruction_count']==245
        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and ir['shader']=='808EE505' and ir['instruction_count']==456
        rows=p['instruction_resolution']; ins=ir['instructions']; attrs=set(p['interpolator_inputs'])
        assert attrs=={'attr0.w','attr0.x','attr0.y','attr0.z','attr1.x','attr1.y','attr1.z','attr2.x','attr2.y','attr2.z','attr3.x','attr3.y','attr4.x','attr4.y','attr4.z'}

        # The source semantics were pinned upstream from the GCN3 instruction reference.
        sem=p['terminal_mrt_expression']['source_semantics']
        s1=sem['v_interp_p1_f32']; s2=sem['v_interp_p2_f32']
        assert s1['equation']==P1_EQ and s2['equation']==P2_EQ
        for s in (s1,s2):
            assert s['source_revision']==SOURCE_REV and s['source_file_sha256']==SOURCE_SHA
            assert s['coefficients']=='RASTER_INTERPOLATION_CONTEXT'
            assert s['text_operand_order']=='IJ_VGPR_FIRST_ATTRIBUTE_SECOND'

        pairs={}
        for x in ins:
            if x['opcode'] not in ('v_interp_p1_f32','v_interp_p2_f32'): continue
            asm=x['assembly'].split('*/',1)[-1].strip()
            m=RX.fullmatch(asm); assert m,(x['index'],asm)
            phase,dst,src,attr=m.groups(); assert attr in attrs,(x['index'],attr)
            pairs.setdefault((dst,attr),[]).append({'phase':int(phase),'src':src,'instruction':x['index']})
        assert len(pairs)==21 and sum(len(v) for v in pairs.values())==42
        bindings=[]; promoted=[]; corroborated=[]
        out=copy.deepcopy(base); op=out['program']; orows=op['instruction_resolution']
        for (dst,attr),items in sorted(pairs.items(), key=lambda kv:min(x['instruction'] for x in kv[1])):
            items=sorted(items,key=lambda x:x['phase'])
            assert [x['phase'] for x in items]==[1,2],((dst,attr),items)
            assert [x['src'] for x in items]==['v0','v1'],((dst,attr),items)
            i1,i2=items[0]['instruction'],items[1]['instruction']
            binding={'destination':dst,'attribute':attr,'p1_instruction':i1,'p2_instruction':i2,
                     'p1_equation':P1_EQ,'p2_equation':P2_EQ,'ij_inputs':{'p1':'v0','p2':'v1'},
                     'coefficients':'RASTER_INTERPOLATION_CONTEXT','source_revision':SOURCE_REV,'source_file_sha256':SOURCE_SHA}
            bindings.append(binding)
            for i in (i1,i2):
                r=orows[i]
                if r['primary_resolution']=='STRUCTURAL_ONLY':
                    r['primary_resolution']='INPUT_PROVENANCE_EXACT'; promoted.append(i)
                else:
                    assert r['primary_resolution']=='EXPRESSION_EXACT',(i,r)
                    corroborated.append(i)
                r['evidence_tags']=sorted(set(r.get('evidence_tags',[])+['GCN_INTERPOLATION_SEMANTICS_SOURCE_EXACT','PIXEL_INTERPOLATOR_INPUT_EXACT']))
        promoted=sorted(promoted); corroborated=sorted(corroborated)
        assert len(promoted)==40 and corroborated==[443,446],(promoted,corroborated)

        op['interpolation_bindings']=bindings
        counts=collections.Counter(r['primary_resolution'] for r in orows)
        structural={i for i,r in enumerate(orows) if r['primary_resolution']=='STRUCTURAL_ONLY'}
        spans=[]
        for lo,hi in contiguous(structural):
            rr=ins[lo:hi+1]; ops=collections.Counter(x['opcode'] for x in rr)
            spans.append({'start_instruction':lo,'end_instruction':hi,'instruction_count':hi-lo+1,
                          'opcode_histogram':dict(sorted(ops.items())),
                          'image_instructions':[x['index'] for x in rr if x['opcode'].startswith('image_')],
                          'branch_instructions':[x['index'] for x in rr if x['opcode'].startswith('s_cbranch') or x['opcode']=='s_branch'],
                          'exec_write_instructions':[x['index'] for x in rr if 'exec' in x.get('defs',[])],
                          'boundary':'STRUCTURAL_ONLY_NO_VALUE_EXPRESSION_PROMOTION'})
        oc=op['coverage']; oc['primary_resolution_counts']=dict(sorted(counts.items()))
        oc['exact_nonstructural_instruction_count']=456-counts['STRUCTURAL_ONLY']
        oc['structural_only_instruction_count']=counts['STRUCTURAL_ONLY']; oc['structural_only_spans']=spans
        oc['interpolation_semantics_promoted_instructions']=promoted
        oc['interpolation_semantics_promoted_instruction_count']=len(promoted)
        oc['interpolation_semantics_corroborated_existing_instructions']=corroborated
        expected={'CONTROL_EXACT':18,'EXPRESSION_EXACT':161,'INPUT_PROVENANCE_EXACT':70,'RECURRENCE_EXACT':36,'STRUCTURAL_ONLY':171}
        assert oc['primary_resolution_counts']==expected,oc
        assert oc['exact_nonstructural_instruction_count']==285 and oc['structural_only_instruction_count']==171
        assert all(not x['opcode'].startswith('v_interp_') for i,x in enumerate(ins) if orows[i]['primary_resolution']=='STRUCTURAL_ONLY')
        out['schema_version']=max(6,int(out.get('schema_version',0)))
        out.setdefault('semantic_boundary',{})['pixel_interpolation']='EXACT_SYMBOLIC_GCN_P1_P2_FOR_ALL_21_PAIRS'
        out['semantic_boundary']['raster_interpolation_coefficient_live_values']='RUNTIME_INPUT_NOT_NUMERICALLY_CAPTURED'
        result=out; result['violations']=[]
    except Exception as exc:
        violations.append(repr(exc)); result={'schema_version':1,'status':'D1_GCN_RENDERER_INTERPOLATION_SEMANTICS_PARTIAL','violations':violations}
    a.output.parent.mkdir(parents=True,exist_ok=True); a.output.write_text(json.dumps(result,indent=2)+'\n')
    print(json.dumps({'status':result.get('status'),'coverage':result.get('program',{}).get('coverage',{}).get('primary_resolution_counts'),
                      'exact_nonstructural':result.get('program',{}).get('coverage',{}).get('exact_nonstructural_instruction_count'),
                      'violations':violations},indent=2))
    return 0 if not violations else 2

if __name__=='__main__': raise SystemExit(main())
