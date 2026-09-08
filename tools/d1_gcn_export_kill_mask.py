#!/usr/bin/env python3
"""Promote canonical GCN persistent-EXEC export kill masks from structural IR.

The detector is deliberately narrow. It only promotes a hard-discard contract when
an exact image sample and cbuffer threshold feed a comparison whose VCC predicate
is removed from a persistent mask copied from initial EXEC, and that mask is then
reapplied to EXEC for MRT export. This is renderer-useful control-flow semantics,
not an appearance or texture-name guess.
"""
from __future__ import annotations
import argparse,json,re
from pathlib import Path

REGPAIR_RE=re.compile(r'^s\[(\d+):(\d+)\]$')

def block_for(ir,i):
    for b in ir['basic_blocks']:
        if b['start_instruction']<=i<=b['end_instruction']:return b
    raise KeyError(i)
def prev_def(ir,reg,before,lo=0):
    for i in range(before-1,lo-1,-1):
        if reg in ir['instructions'][i].get('defs',[]):return ir['instructions'][i]
    return None
def flatten_cb(stage):
    out=[]
    for r in stage['stage']['ps_cbuffers']['items']:out.extend(float(x) for x in r['value'])
    return out

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ir',type=Path,required=True);ap.add_argument('--stage',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    ir=json.load(open(a.ir));sd=json.load(open(a.stage));viol=[];contracts=[]
    try:
        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE'
        assert sd['status']=='D1_CORPUS_MATERIAL_STAGE_EXACT' and len(sd['materials'])==1
        stage=sd['materials'][0]; assert stage['stage']['pixel_shader']==ir['shader']; cb=flatten_cb(stage)
        ins=ir['instructions']
        inits={}
        for x in ins:
            if x['opcode']=='s_mov_b64' and len(x['operands'])>=2 and x['operands'][1]=='exec' and REGPAIR_RE.match(x['operands'][0]):
                inits[x['operands'][0]]=x['index']
        for k in ins:
            if k['opcode']!='s_andn2_b64' or len(k['operands'])<3:continue
            mask=k['operands'][0]
            if mask not in inits or k['operands'][1]!=mask or k['operands'][2] not in ('vcc','vcc_lo','vcc_hi'):continue
            uses=[]
            for x in ins[k['index']+1:]:
                if x['opcode']=='s_and_b64' and len(x['operands'])>=3 and x['operands'][0]=='exec' and x['operands'][1]=='exec' and x['operands'][2]==mask:
                    uses.append(x['index'])
            if not uses:continue
            consume=uses[0]
            exports=[];last_mask_apply=None;last_exec_write=None
            for x in ins[consume:]:
                if x['opcode']=='s_and_b64' and len(x['operands'])>=3 and x['operands'][0]=='exec' and x['operands'][1]=='exec' and x['operands'][2]==mask:
                    last_mask_apply=x['index'];last_exec_write=('DIRECT_AND',x['index'])
                elif x['opcode']=='s_mov_b64' and len(x['operands'])>=2 and x['operands'][0]=='exec' and x['operands'][1]==mask:
                    last_mask_apply=x['index'];last_exec_write=('DIRECT_MOV',x['index'])
                elif 'exec' in x.get('defs',[]):
                    if x['opcode']=='s_wqm_b64' and last_mask_apply is not None:
                        last_exec_write=('WQM_OF_MASKED_EXEC',x['index'])
                    else:
                        last_exec_write=('OTHER_EXEC_WRITE',x['index']);last_mask_apply=None
                if x['opcode']=='exp' and x['operands'] and x['operands'][0].startswith('mrt') and last_exec_write and last_mask_apply is not None:
                    exports.append({'instruction':x['index'],'target':x['operands'][0],'exec_relation':last_exec_write[0],'exec_write_instruction':last_exec_write[1],'originating_mask_apply_instruction':last_mask_apply})
            if not exports:continue
            b=block_for(ir,k['index']);lo=b['start_instruction']
            cmp=prev_def(ir,'vcc',k['index'],lo)
            assert cmp and cmp['opcode']=='v_cmp_gt_f32' and len(cmp['operands'])==3 and cmp['operands'][0]=='vcc' and cmp['operands'][1]=='0',cmp
            valreg=cmp['operands'][2]; assert valreg.startswith('v')
            sub=prev_def(ir,valreg,cmp['index'],lo)
            assert sub and sub['opcode']=='v_subrev_f32' and sub['operands'][0]==valreg and len(sub['operands'])==3,sub
            threshold_reg=sub['operands'][1];sample_reg=sub['operands'][2];assert sample_reg==valreg and threshold_reg.startswith('s')
            sample=prev_def(ir,sample_reg,sub['index'],lo); assert sample and 'image' in sample,sample
            tex=sample['image']['textures'];assert len(tex)==1,tex
            load=prev_def(ir,threshold_reg,sub['index'],lo);assert load and load['opcode']=='s_buffer_load_dword',load
            assert load['operands'][0]==threshold_reg and len(load['operands'])>=3
            off=int(load['operands'][2],0);assert 0<=off<len(cb),(off,len(cb));threshold=cb[off]
            contracts.append({
              'mask_register':mask,'mask_initialized_instruction':inits[mask],'kill_instruction':k['index'],'first_exec_consume_instruction':consume,
              'governed_exports':exports,
              'predicate':{'compare_instruction':cmp['index'],'compare':'0 > (threshold - sample)','equivalent':'sample > threshold','threshold_load_instruction':load['index'],'constant_scalar_index':off,'threshold':threshold,
                           'sample_instruction':sample['index'],'texture_indices':tex,'dmask_channels':sample['image'].get('dmask_channels')},
              'mask_update':'persistent_export_mask &= ~predicate','discard_when':'sample > threshold','survive_when':'sample <= threshold',
              'proof':'The sampled scalar defines the VCC predicate immediately feeding s_andn2 on a persistent mask copied from initial EXEC; that mask is later reapplied to EXEC for the listed MRT exports. WQM-derived exports remain explicitly marked WQM rather than collapsed to direct masking.'})
        assert contracts,'no export kill mask contract found'
    except Exception as ex:viol.append(repr(ex))
    out={'schema_version':1,'status':'D1_GCN_EXPORT_KILL_MASK_CONTRACT_COMPLETE' if contracts and not viol else 'D1_GCN_EXPORT_KILL_MASK_CONTRACT_PARTIAL','shader':ir.get('shader'),'material':sd.get('materials',[{}])[0].get('material') if sd.get('materials') else None,'contracts':contracts,'violations':viol,
         'policy':'Promotion is limited to canonical persistent-EXEC-mask kill patterns whose image sample, comparison, cbuffer threshold, mask update and MRT EXEC relationship are structurally connected. No visual/filename heuristic is used.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
