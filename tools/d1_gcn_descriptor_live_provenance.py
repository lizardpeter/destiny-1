#!/usr/bin/env python3
"""Recover live D1 GFX7 resource/sampler descriptor provenance at image instructions.

Unlike a static InputUsageSlot lookup, this pass tracks the physical SGPR contents as
native scalar loads and moves overwrite them.  It consumes source-proven GFX7 offset
and descriptor-width semantics and cross-checks every recovered t#/sampler use against
the existing exact image-usage census.

The result is destination-neutral decoder IR suitable for both Blender adapters and a
Rust renderer.  Texture visual roles remain outside this layer.
"""
from __future__ import annotations
import argparse, collections, copy, json, re
from pathlib import Path

RANGE_RE=re.compile(r'^s\[(\d+):(\d+)\]$')
SINGLE_RE=re.compile(r'^s(\d+)$')
SGPR_RANGE_RE=re.compile(r'\bs\[(\d+)\s*:\s*(\d+)\]')


def regs(tok):
    m=RANGE_RE.match(tok)
    if m:return list(range(int(m.group(1)),int(m.group(2))+1))
    m=SINGLE_RE.match(tok)
    return [int(m.group(1))] if m else []


def slot_width(name, sem):
    if name=='ImmResource':return sem['mimg_descriptor_widths_dwords']['resource']
    if name=='ImmSampler':return sem['mimg_descriptor_widths_dwords']['sampler']
    if name=='ImmConstBuffer':return 4
    if name in ('PtrExtendedUserData','PtrResourceTable'):return 2
    return 1


def logical_words(usage, sem):
    out={}
    for s in usage['slots']:
        start=int(s['start_register']);w=slot_width(s['usage_name'],sem)
        base={
          'kind':s['usage_name'],'api_slot':int(s['api_slot']),
          'logical_start':start,'usage_slot_index':int(s['index']),
          'chunk_mask':int(s.get('chunk_mask',0)),
        }
        for i in range(w):out[start+i]={**base,'word':i}
    return out


def coherent(phys, rr, kind=None):
    vals=[phys.get(r) for r in rr]
    if not vals or any(v is None for v in vals):return None
    keys={(v['kind'],v['api_slot'],v.get('origin_kind'),v.get('producer_instruction'),v.get('logical_start'),v.get('table_offset_dwords')) for v in vals}
    if len(keys)!=1:return None
    v=copy.deepcopy(vals[0])
    if kind and v['kind']!=kind:return None
    if [x.get('word') for x in vals]!=list(range(len(vals))):return None
    return v


def copy_regs(phys,dst,src,producer):
    vals=[copy.deepcopy(phys.get(r)) for r in src]
    for r in dst:phys.pop(r,None)
    for d,v in zip(dst,vals):
        if v is not None:
            v['last_copy_instruction']=producer;phys[d]=v


def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--ir',type=Path,required=True)
    ap.add_argument('--shader-extract',type=Path,required=True)
    ap.add_argument('--image-usage',type=Path,required=True)
    ap.add_argument('--descriptor-semantics',type=Path,required=True)
    ap.add_argument('--shader',default='808EE505')
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args()

    ir=json.load(open(a.ir));ext=json.load(open(a.shader_extract));iu=json.load(open(a.image_usage));ds=json.load(open(a.descriptor_semantics))
    violations=[];payload={}
    try:
        sh=a.shader.upper().removeprefix('0X').zfill(8)
        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and ir['shader']==sh
        assert ds['status']=='D1_GFX7_DESCRIPTOR_SEMANTICS_SOURCE_PROVEN' and not ds['violations']
        sem=ds['proof'];assert sem['architecture']=='GFX7_GFX700'
        assert sem['smrd_immediate_offset_unit']=='DWORD' and sem['resident_user_sgpr_count']==16
        assert sem['mimg_descriptor_widths_dwords']=={'resource':8,'sampler':4}
        er=[x for x in ext['shaders'] if str(x['shader']).upper()==sh]
        assert len(er)==1 and er[0].get('usage'),er
        usage=er[0]['usage'];logical=logical_words(usage,sem)
        ur=[x for x in iu['shaders'] if str(x['shader']).upper()==sh]
        assert iu['status']=='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT' and len(ur)==1 and ur[0]['unmatched_image_instruction_count']==0
        exact_by_addr={str(x['address']).upper().zfill(12):x for x in ur[0]['instructions']}

        resident=int(sem['resident_user_sgpr_count'])
        phys={}
        for r,p in logical.items():
            if r<resident:
                phys[r]={**copy.deepcopy(p),'origin_kind':'ENTRY_RESIDENT','producer_instruction':None}

        loads=[];images=[];all_exact_loads=[]
        for x in ir['instructions']:
            i=int(x['index']);op=x['opcode'];ops=x['operands']
            # Exact scalar copies preserve provenance word-for-word.
            if op=='s_mov_b64' and len(ops)>=2:
                d,s=regs(ops[0]),regs(ops[1]);
                if d and s:copy_regs(phys,d,s,i)
            elif op=='s_mov_b32' and len(ops)>=2:
                d,s=regs(ops[0]),regs(ops[1]);
                if d and s:copy_regs(phys,d,s,i)

            if op in ('s_load_dwordx4','s_load_dwordx8') and len(ops)>=3:
                dst,src=regs(ops[0]),regs(ops[1]);off=int(ops[2],0)
                expected=int(sem['scalar_load_widths_dwords'][op])
                assert len(dst)==expected,(i,op,dst)
                srcp=coherent(phys,src)
                for r in dst:phys.pop(r,None)
                ev={'instruction':i,'address':x['address_hex'],'opcode':op,'destination_sgprs':dst,
                    'source_sgprs':src,'immediate_offset_dwords':off,'source_provenance':srcp,'resolution':'UNRESOLVED'}
                if srcp and srcp['kind']=='PtrExtendedUserData':
                    lstart=int(sem['extended_user_data_logical_base_dword'])+off
                    vals=[logical.get(lstart+j) for j in range(expected)]
                    if all(v is not None for v in vals):
                        slotkeys={(v['kind'],v['api_slot'],v['logical_start'],v['usage_slot_index']) for v in vals}
                        if len(slotkeys)==1 and [v['word'] for v in vals]==list(range(expected)):
                            for d,v in zip(dst,vals):
                                phys[d]={**copy.deepcopy(v),'origin_kind':'EXTENDED_USER_DATA_LOAD','producer_instruction':i,
                                         'extended_offset_dwords':off}
                            q=vals[0]
                            ev.update({'resolution':'EXACT_EXTENDED_USER_DATA_SLOT','logical_start':lstart,
                                       'resolved_kind':q['kind'],'api_slot':q['api_slot'],'usage_slot_index':q['usage_slot_index']})
                            all_exact_loads.append(i)
                elif srcp and srcp['kind']=='PtrResourceTable' and expected==sem['mimg_descriptor_widths_dwords']['resource']:
                    stride=int(sem['mimg_descriptor_widths_dwords']['resource'])
                    if off%stride==0:
                        ti=int(srcp['api_slot'])+off//stride
                        base={'kind':'ResourceTableResource','api_slot':ti,'logical_start':None,
                              'usage_slot_index':srcp['usage_slot_index'],'origin_kind':'RESOURCE_TABLE_LOAD',
                              'producer_instruction':i,'table_offset_dwords':off}
                        for j,d in enumerate(dst):phys[d]={**base,'word':j}
                        ev.update({'resolution':'EXACT_RESOURCE_TABLE_DESCRIPTOR','texture_index':ti,
                                   'table_entry_index':off//stride,'descriptor_width_dwords':stride})
                        all_exact_loads.append(i)
                loads.append(ev)

            if 'image' in x:
                exact=exact_by_addr.get(str(x['address_hex']).upper())
                assert exact is not None,(i,x['address_hex'])
                ranges=[list(range(int(m.group(1)),int(m.group(2))+1)) for m in SGPR_RANGE_RE.finditer(x['assembly'])]
                resource=[];sampler=[]
                for rr in ranges:
                    p=coherent(phys,rr)
                    if p is None:continue
                    if len(rr)==sem['mimg_descriptor_widths_dwords']['resource'] and p['kind'] in ('ImmResource','ResourceTableResource'):
                        resource.append({'sgprs':rr,**p})
                    if len(rr)==sem['mimg_descriptor_widths_dwords']['sampler'] and p['kind']=='ImmSampler':
                        sampler.append({'sgprs':rr,**p})
                assert len(resource)==1 and len(sampler)==1,(i,resource,sampler,x['assembly'])
                r,s=resource[0],sampler[0]
                assert exact['resources']==[{
                    'sgpr':f"s[{r['sgprs'][0]}:{r['sgprs'][-1]}]",'start_register':r['sgprs'][0],'end_register':r['sgprs'][-1],
                    'texture_index':r['api_slot'],'provenance_kind':r['kind']}],(i,exact['resources'],r)
                assert exact['samplers']==[{
                    'sgpr':f"s[{s['sgprs'][0]}:{s['sgprs'][-1]}]",'start_register':s['sgprs'][0],'end_register':s['sgprs'][-1],
                    'sampler_index':s['api_slot'],'provenance_kind':'ImmSampler'}],(i,exact['samplers'],s)
                images.append({
                  'instruction':i,'address':x['address_hex'],'opcode':x['opcode'],'dmask_channels':x['image'].get('dmask_channels'),
                  'texture_index':r['api_slot'],'resource_descriptor':r,
                  'sampler_index':s['api_slot'],'sampler_descriptor':s,
                  'crosscheck':'MATCHES_D1_GCN_IMAGE_RESOURCE_USAGE_EXACT'
                })

        assert len(images)==ur[0]['image_instruction_count']==14,(len(images),ur[0]['image_instruction_count'])
        assert len(set(all_exact_loads))==12,(all_exact_loads,loads)
        # Target completeness fixtures: all six t# resource-table entries and all
        # four spilled samplers plus both spilled constant-buffer descriptors appear.
        rt={q['texture_index']:q for q in loads if q['resolution']=='EXACT_RESOURCE_TABLE_DESCRIPTOR'}
        assert set(rt)==set(range(6)),rt
        extloads=[q for q in loads if q['resolution']=='EXACT_EXTENDED_USER_DATA_SLOT']
        extkeys={(q['resolved_kind'],q['api_slot'],q['logical_start']) for q in extloads}
        assert extkeys=={
          ('ImmSampler',3,16),('ImmSampler',4,20),('ImmSampler',5,24),('ImmSampler',6,28),
          ('ImmConstBuffer',0,32),('ImmConstBuffer',12,36)},extkeys
        sampler_origins=collections.Counter(q['sampler_descriptor']['origin_kind'] for q in images)
        assert sampler_origins=={'ENTRY_RESIDENT':9,'EXTENDED_USER_DATA_LOAD':5},sampler_origins

        payload={
          'shader':sh,'architecture':'GFX7_GFX700','image_instruction_count':len(images),
          'descriptor_load_count':len(loads),'exact_descriptor_load_count':len(set(all_exact_loads)),
          'exact_descriptor_load_instructions':sorted(set(all_exact_loads)),
          'entry_usage_slots':usage['slots'],'descriptor_loads':loads,'image_live_bindings':images,
          'sampler_origin_counts':dict(sorted(sampler_origins.items())),
          'semantic_boundary':{
            'live_descriptor_provenance':'EXACT',
            'resource_table_texture_index':'EXACT_CROSSCHECKED_WITH_EXISTING_IMAGE_USAGE_CENSUS',
            'extended_user_data_logical_slot':'EXACT_GFX7_USER_SGPR_PLUS_INPUT_USAGE_LAYOUT',
            'texture_visual_roles':'WITHHELD',
            'sampler_state_semantic_decode':'DESCRIPTOR_SLOT_EXACT_STATE_BITS_NOT_DECODED_HERE'
          }
        }
    except Exception as exc:
        violations.append(repr(exc))

    out={'schema_version':1,'status':'D1_GCN_DESCRIPTOR_LIVE_PROVENANCE_EXACT' if payload and not violations else 'D1_GCN_DESCRIPTOR_LIVE_PROVENANCE_PARTIAL',
         'proof':payload,'violations':violations,
         'policy':'Physical SGPR descriptor provenance is replayed instruction-by-instruction. Dynamic PtrExtendedUserData/PtrResourceTable loads override entry SGPR roles. Every image binding is cross-checked against the independently exact image-usage census; no visual texture role is inferred.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({'status':out['status'],'image_instruction_count':payload.get('image_instruction_count') if payload else None,
                      'exact_descriptor_loads':payload.get('exact_descriptor_load_instructions') if payload else None,
                      'sampler_origin_counts':payload.get('sampler_origin_counts') if payload else None,'violations':violations},indent=2))
    return 0 if not violations else 2


if __name__=='__main__':
    raise SystemExit(main())
