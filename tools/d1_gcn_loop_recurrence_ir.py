#!/usr/bin/env python3
from __future__ import annotations
import argparse,json,re
from pathlib import Path
VREG=re.compile(r'^v\d+$')

def last_def(ins,reg,before):
    for x in reversed(ins[:before]):
        if reg in x.get('defs',[]): return x
    return None

def mat_scalar(cbuf,instr):
    rows=[r for r in cbuf['loads'] if r['instruction']==instr and r.get('resolution')=='EXACT_MATERIAL_PS_B0']
    if len(rows)!=1 or len(rows[0].get('material_values') or [])!=1: raise ValueError(f'instruction {instr}: exact single material scalar required')
    return rows[0]['material_values'][0]

def main():
    ap=argparse.ArgumentParser();ap.add_argument('--ir',type=Path,required=True);ap.add_argument('--mimg',type=Path,required=True);ap.add_argument('--control-semantics',type=Path,required=True);ap.add_argument('--cbuffer-provenance',type=Path,required=True);ap.add_argument('-o','--output',type=Path,required=True);a=ap.parse_args()
    ir=json.load(open(a.ir));mi=json.load(open(a.mimg));sem=json.load(open(a.control_semantics));cb=json.load(open(a.cbuffer_provenance));viol=[];rec=[]
    try:
        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and int(ir.get('schema_version',0))>=2
        assert mi['status']=='D1_GCN_MIMG_ADDRESS_PROVENANCE_EXACT' and not mi['violations']
        assert sem['status']=='D1_GCN_CONTROL_SEMANTICS_SOURCE_PROVEN' and not sem['violations']
        assert cb['status']=='D1_GCN_CBUFFER_PROVENANCE_EXACT' and not cb['violations']
        ins=ir['instructions']; by={b['id']:b for b in ir['basic_blocks']}
        loops=ir['control_flow'].get('back_edges',[]); assert len(loops)==1,loops
        e=loops[0]; start=by[e['to_block']]['start_instruction']; end=by[e['from_block']]['end_instruction']; body=ins[start:end+1]
        expect=['v_cmp_gt_i32','s_mov_b64','s_andn2_b64','s_andn2_b64','s_cbranch_scc0','s_and_b64','v_mad_f32','v_mad_f32','s_waitcnt','image_sample_d','v_subrev_f32','s_waitcnt','v_cmp_gt_f32','s_and_saveexec_b64','v_add_f32','s_cbranch_execz','v_mov_b32','v_mov_b32','v_mov_b32','v_mov_b32','s_andn2_b64','v_add_i32','v_mov_b32','s_mov_b64','s_branch']
        assert [x['opcode'] for x in body]==expect,[x['opcode'] for x in body]
        h,sav,done,live,br,activate,c0,c1,_,sample,depth,_,hit,ifsave,bracket,ifempty,p0,p1,p2,p3,els,inc,prev,restore,back=body
        assert h['operands'][0]=='vcc' and len(h['operands'])==3
        step_count,counter=h['operands'][1],h['operands'][2]
        saved=sav['operands'][0]; assert sav['operands']==[saved,'exec']
        assert done['operands']==['exec',saved,'vcc']
        live_mask=live['operands'][0]; assert live['operands']==[live_mask,live_mask,'exec']
        assert activate['operands']==['exec',saved,live_mask]
        assert c0['operands'][0]==c0['operands'][3] and c1['operands'][0]==c1['operands'][3]
        coord_s,coord_t=c0['operands'][0],c1['operands'][0]
        assert c0['operands'][1].startswith('-') and c1['operands'][1]==c0['operands'][1]
        step=c0['operands'][1][1:]; dir_s=c0['operands'][2];dir_t=c1['operands'][2]
        mrows=[r for r in mi['rows'] if r['instruction']==sample['index']]; assert len(mrows)==1,mrows
        mr=mrows[0]; assert mr['effective_address_registers'][-2:]==[coord_s,coord_t],(mr,coord_s,coord_t)
        assert mr['effective_address_word_count']==6
        sample_value=sample['operands'][0]
        threshold=depth['operands'][0]; assert depth['operands']==[threshold,step,threshold]
        assert hit['operands']==['vcc',sample_value,threshold]
        inner_saved=ifsave['operands'][0]; assert ifsave['operands']==[inner_saved,'vcc']
        assert bracket['operands']==[bracket['operands'][0],step,threshold]
        assert els['operands']==['exec',inner_saved,'exec']
        assert inc['operands'][0]==counter and inc['operands'][2:] == ['1',counter]
        assert prev['operands']==[prev['operands'][0],sample_value]
        prev_sample=prev['operands'][0]
        assert p0['operands']==[p0['operands'][0],prev_sample]
        assert p1['operands']==[p1['operands'][0],threshold]
        assert p2['operands']==[p2['operands'][0],sample_value]
        terminal=p3['operands'][1]; assert p3['operands'][0]==counter
        assert restore['operands']==['exec',inner_saved]
        init={r:last_def(ins,r,start) for r in [counter,prev_sample,threshold,coord_s,coord_t,p0['operands'][0],p1['operands'][0],p2['operands'][0],bracket['operands'][0],live_mask]}
        assert init[counter]['opcode']=='v_mov_b32' and init[counter]['operands'][1]=='0'
        assert init[prev_sample]['opcode']=='v_mov_b32' and init[prev_sample]['operands'][1]=='1.0'
        assert init[threshold]['opcode']=='v_mov_b32' and init[threshold]['operands'][1]=='1.0'
        assert init[coord_s]['opcode']=='v_mov_b32' and init[coord_t]['opcode']=='v_mov_b32'
        coord_s0=init[coord_s]['operands'][1];coord_t0=init[coord_t]['operands'][1]
        for r in [p0['operands'][0],p1['operands'][0],p2['operands'][0],bracket['operands'][0]]:
            assert init[r]['opcode']=='v_mov_b32' and init[r]['operands'][1]=='0'
        termdef=last_def(ins,terminal,start); assert termdef and termdef['opcode']=='v_add_i32' and termdef['operands'][0]==terminal and termdef['operands'][2:] == ['1',step_count]
        stepdef=last_def(ins,step,start); assert stepdef and stepdef['opcode']=='v_rcp_f32'
        float_count=stepdef['operands'][1]; fcdef=last_def(ins,float_count,stepdef['index']); assert fcdef and fcdef['opcode']=='v_cvt_f32_i32' and fcdef['operands'][1]==step_count
        count_cvt=last_def(ins,step_count,start); assert count_cvt and count_cvt['opcode']=='v_cvt_i32_f32'
        count_mad=last_def(ins,count_cvt['operands'][1],count_cvt['index']); assert count_mad and count_mad['opcode']=='v_mad_f32' and count_mad['operands'][0]==step_count
        count_factor=count_mad['operands'][1]; count_delta_reg=count_mad['operands'][2]; count_hi_s=count_mad['operands'][3]
        delta_def=last_def(ins,count_delta_reg,count_mad['index']); assert delta_def and delta_def['opcode']=='v_subrev_f32' and delta_def['operands'][0]==count_delta_reg
        assert delta_def['operands'][1]==count_hi_s
        low_reg=delta_def['operands'][2]; low_def=last_def(ins,low_reg,delta_def['index']); assert low_def and low_def['opcode']=='v_mov_b32'
        count_lo_s=low_def['operands'][1]
        hi_def=last_def(ins,count_hi_s,count_mad['index']); lo_def=last_def(ins,count_lo_s,low_def['index'])
        assert hi_def and lo_def and hi_def['opcode'].startswith('s_buffer_load_dword') and lo_def['opcode'].startswith('s_buffer_load_dword')
        chi=mat_scalar(cb,hi_def['index']); clo=mat_scalar(cb,lo_def['index']); assert chi['value']==30.0 and clo['value']==4.0
        post=ins[end+1:end+17]
        assert [x['opcode'] for x in post[:16]]==['s_mov_b64','v_sub_f32','v_sub_f32','v_sub_f32','v_cmp_neq_f32','s_and_saveexec_b64','v_mul_f32','v_mad_f32','v_rcp_f32','v_mul_f32','s_andn2_b64','v_mov_b32','s_mov_b64','v_sub_f32','v_mad_f32','v_mad_f32']
        rr={'loop_start_instruction':start,'loop_end_instruction':end,'back_edge':e,'step_count_register':step_count,'counter_register':counter,'terminal_counter_register':terminal,
            'initial_state':{'counter':0,'previous_sample':1.0,'threshold':1.0,'coord_s':coord_s0,'coord_t':coord_t0,'bracket_depth':0.0,'bracket_previous_sample':0.0,'bracket_threshold':0.0,'bracket_current_sample':0.0},
            'adaptive_step_count':{'expression':f'v_cvt_i32_f32({chi["value"]} + ({clo["value"]} - {chi["value"]}) * {count_factor}@{count_mad["index"]})','factor_register':count_factor,'factor_use_instruction':count_mad['index'],'material_b0_constants':[chi,clo],'conversion_instruction':count_cvt['index'],'step_size_expression':f'{step} = rcp(float({step_count}))','step_size_instruction':stepdef['index']},
            'mask_recurrence':{'candidate_predicate':f'{step_count} > {counter}','completed_mask':'header_exec & ~candidate_predicate','persistent_live_mask_update':f'{live_mask}_next = {live_mask} & ~completed_mask','wave_exit_condition':f'{live_mask}_next == 0','body_exec':'header_exec & persistent_live_mask_next'},
            'per_iteration_recurrence':{'coord_s':f'{coord_s}_next = {coord_s} - {step} * {dir_s}','coord_t':f'{coord_t}_next = {coord_t} - {step} * {dir_t}','threshold':f'{threshold}_next = {threshold} - {step}','sample':{'instruction':sample['index'],'value_register':sample_value,'texture_index':mr['texture_index'],'texture':mr['texture'],'sampler_index':mr['sampler_index'],'resource_class':mr['resource_class'],'address_registers':mr['effective_address_registers'],'address_components':mr['effective_address_components'],'equation':f'{sample_value} = SAMPLE_D_2D(t{mr["texture_index"]}, gradients=v35..v38, coord=({coord_s}_next,{coord_t}_next)).x'},'hit_predicate':f'{sample_value} > {threshold}_next','hit_path':{bracket['operands'][0]:f'{step} + {threshold}_next',p0['operands'][0]:prev_sample,p1['operands'][0]:f'{threshold}_next',p2['operands'][0]:sample_value,counter:terminal},'miss_path':{counter:f'{counter} + 1',prev_sample:sample_value}},
            'termination':{'false_path_progresses_counter_by_one':True,'hit_path_forces_counter_past_limit':f'{terminal} = {step_count} + 1','per_lane_sample_bound':f'max({step_count}, 0)'},
            'post_loop_refinement':{'a':f"{post[1]['operands'][0]} = {post[1]['operands'][1]} - {post[1]['operands'][2]}",'b':f"{post[2]['operands'][0]} = {post[2]['operands'][1]} - {post[2]['operands'][2]}",'denominator':f"{post[3]['operands'][0]} = {post[3]['operands'][1]} - {post[3]['operands'][2]}",'fraction':'denominator != 0 ? ((bracket_threshold * a - bracket_depth * b) / denominator) : 0','depth_fraction':'1 - fraction','output_coordinates':{post[14]['operands'][0]:f'{coord_s0} - depth_fraction * {dir_s}',post[15]['operands'][0]:f'{coord_t0} - depth_fraction * {dir_t}'},'instruction_range':[post[0]['index'],post[15]['index']]},
            'classification':'EXACT_ADAPTIVE_2D_SAMPLE_INTERSECTION_RECURRENCE','semantic_role':'WITHHELD_NO_SOURCE_NAME'}
        rec.append(rr)
    except Exception as e: viol.append(repr(e))
    out={'schema_version':1,'status':'D1_GCN_LOOP_RECURRENCE_EXACT' if rec and not viol else 'D1_GCN_LOOP_RECURRENCE_PARTIAL','shader':ir.get('shader'),'recurrences':rec,'violations':viol,'semantic_boundary':{'control_flow_and_numeric_recurrence':'SOURCE_AND_INSTRUCTION_EXACT','2d_sample_address_span':'SOURCE_AND_BINDING_EXACT','developer_visual_role_name':'WITHHELD'},'policy':'Loop recurrences are promoted only when the CFG back-edge, EXEC/SCC mask semantics, dimension-aware MIMG payload, nested lane merge, and initialization/termination state all close exactly. No finite unroll count or visual role is guessed.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
