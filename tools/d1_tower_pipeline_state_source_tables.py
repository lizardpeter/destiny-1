#!/usr/bin/env python3
"""Decode pinned Tiger PipelineState source tables for Tower-selected indices.

Consumes d1_tower_material_state4_source_correlation/v1 and exact pinned Alkahest
table files.  Only indices actually selected in the Tower material populations are
decoded.

This is a source-table report, not a global D1 behavioral promotion.
"""
from __future__ import annotations
import argparse,hashlib,json,re,struct
from pathlib import Path

RASTER=struct.Struct('<IIiiffiiiiI')   # PaddedRasterizerState, 44 bytes
BIAS=struct.Struct('<Iiff')            # ShortDepthBias, 16 bytes

FILL={2:'WIREFRAME',3:'SOLID'}
CULL={1:'NONE',2:'FRONT',3:'BACK'}

def selected_indices(corr, lane):
    out=set()
    for d in (corr.get('domains') or {}).values():
        rows=d.get('lanes') or []
        r=next((x for x in rows if int(x['lane_index'])==lane),None)
        if not r:continue
        for k,n in (r.get('selected_low7_index_counts') or {}).items():
            if k!='NONE' and int(n)>0:out.add(int(k))
    return sorted(out)

def blend_blocks(text):
    pat=re.compile(r'QuadBlendState \{ unk0: (\d+), render_targets: \[\n(.*?)(?=^QuadBlendState \{|\Z)',re.M|re.S)
    out={}
    rtpat=re.compile(
        r'RenderTargetBlendDesc \{ blend_enable: BOOL\((\d+)\), src_blend: ([A-Za-z0-9_]+), '
        r'dest_blend: ([A-Za-z0-9_]+), blend_op: ([A-Za-z0-9_]+), '
        r'src_blend_alpha: ([A-Za-z0-9_]+), dest_blend_alpha: ([A-Za-z0-9_]+), '
        r'blend_op_alpha: ([A-Za-z0-9_]+), render_target_write_mask: (\d+) \}'
    )
    for sm in pat.finditer(text):
        idx=int(sm.group(1)); body=sm.group(2); targets=[]
        for m in rtpat.finditer(body):
            targets.append({
                'blend_enable':bool(int(m.group(1))),
                'src_blend':m.group(2),'dest_blend':m.group(3),'blend_op':m.group(4),
                'src_blend_alpha':m.group(5),'dest_blend_alpha':m.group(6),'blend_op_alpha':m.group(7),
                'render_target_write_mask':int(m.group(8)),
            })
        out[idx]={'index':idx,'render_targets':targets,'target_count':len(targets)}
    return out

def depth_blocks(text):
    pat=re.compile(r'^(\d+) DepthStencilDesc \{\n(.*?)(?=^\d+ DepthStencilDesc \{|\Z)',re.M|re.S)
    out={}
    for m in pat.finditer(text):
        idx=int(m.group(1));b=m.group(2)
        def one(name,default=None):
            q=re.search(rf'^    {re.escape(name)}: ([^,]+),',b,re.M)
            return q.group(1) if q else default
        out[idx]={
            'index':idx,
            'depth_enable':one('depth_enable'),
            'depth_write_mask':one('depth_write_mask'),
            'depth_func':one('depth_func'),
            'stencil_enable':one('stencil_enable'),
            'stencil_read_mask':one('stencil_read_mask'),
            'stencil_write_mask':one('stencil_write_mask'),
            'source_block':f'{idx} DepthStencilDesc {{\n{b}'.rstrip(),
        }
    return out

def raster_desc(raw,idx):
    vals=RASTER.unpack_from(raw,idx*RASTER.size)
    fill,cull,front,db,dbc,slope,depthclip,scissor,msaa,aaline,pad=vals
    return {
        'index':idx,'fill_mode_raw':fill,'fill_mode':FILL.get(fill,f'UNKNOWN_{fill}'),
        'cull_mode_raw':cull,'cull_mode':CULL.get(cull,f'UNKNOWN_{cull}'),
        'front_counter_clockwise':bool(front),'depth_bias_in_base_rasterizer':db,
        'depth_bias_clamp_in_base_rasterizer':dbc,'slope_scaled_depth_bias_in_base_rasterizer':slope,
        'depth_clip_enable':bool(depthclip),'scissor_enable':bool(scissor),
        'multisample_enable_table_value':bool(msaa),'antialiased_line_enable':bool(aaline),
        'source_padding_u32':pad,
    }

def bias_desc(raw,idx):
    unk,depth,slope,clamp=BIAS.unpack_from(raw,idx*BIAS.size)
    return {'index':idx,'unk0_u32':unk,'depth_bias':depth,'slope_scaled_depth_bias':slope,'depth_bias_clamp':clamp}

def main():
    ap=argparse.ArgumentParser()
    ap.add_argument('--correlation',type=Path,required=True)
    ap.add_argument('--blend-text',type=Path,required=True)
    ap.add_argument('--depth-text',type=Path,required=True)
    ap.add_argument('--rasterizer-bin',type=Path,required=True)
    ap.add_argument('--depth-bias-bin',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()

    c=json.loads(a.correlation.read_text());v=[]
    if c.get('status')!='D1_TOWER_MATERIAL_STATE4_SOURCE_CORRELATION_EXACT' or c.get('violations'):
        v.append('state4 source correlation not exact')

    bt=a.blend_text.read_text();dt=a.depth_text.read_text()
    rb=a.rasterizer_bin.read_bytes();db=a.depth_bias_bin.read_bytes()
    blends=blend_blocks(bt);depths=depth_blocks(dt)
    if len(rb)%RASTER.size or len(rb)//RASTER.size!=9:v.append(f'rasterizer table size/count drift {len(rb)}')
    if len(db)%BIAS.size or len(db)//BIAS.size!=9:v.append(f'depth-bias table size/count drift {len(db)}')
    if len(depths)!=83:v.append(f'depth/stencil source descriptor count {len(depths)} != 83')

    sels={i:selected_indices(c,i) for i in range(4)}
    tables={'blend':[],'depth_stencil':[],'rasterizer':[],'depth_bias':[]}

    for idx in sels[0]:
        x=blends.get(idx)
        if x is None:v.append(f'blend index {idx} absent from source table')
        else:tables['blend'].append(x)
    for idx in sels[1]:
        x=depths.get(idx)
        if x is None:v.append(f'depth/stencil index {idx} absent from source table')
        else:tables['depth_stencil'].append(x)
    for idx in sels[2]:
        if idx>=len(rb)//RASTER.size:v.append(f'rasterizer index {idx} out of range')
        else:tables['rasterizer'].append(raster_desc(rb,idx))
    for idx in sels[3]:
        if idx>=len(db)//BIAS.size:v.append(f'depth-bias index {idx} out of range')
        else:tables['depth_bias'].append(bias_desc(db,idx))

    out={
        'schema':'d1_tower_pipeline_state_source_tables/v1',
        'status':'D1_TOWER_PIPELINE_STATE_SOURCE_TABLES_EXACT' if not v else 'D1_TOWER_PIPELINE_STATE_SOURCE_TABLES_PARTIAL',
        'selected_indices':{
            'blend_state':sels[0],
            'depth_stencil_state':sels[1],
            'rasterizer_state':sels[2],
            'depth_bias_state':sels[3],
        },
        'source_tables':tables,
        'source_evidence':{
            'alkahest_commit':'c632a562e88b5b805098152658b915d1c59f0f9a',
            'blend_text_sha256':hashlib.sha256(a.blend_text.read_bytes()).hexdigest(),
            'depth_text_sha256':hashlib.sha256(a.depth_text.read_bytes()).hexdigest(),
            'rasterizer_bin_sha256':hashlib.sha256(rb).hexdigest(),
            'rasterizer_record_bytes':RASTER.size,'rasterizer_record_count':len(rb)//RASTER.size,
            'depth_bias_bin_sha256':hashlib.sha256(db).hexdigest(),
            'depth_bias_record_bytes':BIAS.size,'depth_bias_record_count':len(db)//BIAS.size,
            'depth_stencil_descriptor_count':len(depths),
        },
        'promotion':'SOURCE_CORRELATED_ONLY_EXCEPT_SEPARATELY_PROMOTED_D1_BLEND_FIXTURES',
        'violations':v,
        'semantic_boundary':{
            'selected_indices':'EXACT_D1_BYTES_PLUS_PINNED_SELECTOR_SYNTAX',
            'table_descriptors':'EXACT_PINNED_TIGER_SOURCE',
            'global_d1_behavior_for_unpromoted_indices':'WITHHELD',
            'pass_order_framebuffer_ownership':'WITHHELD',
        },
        'policy':'Descriptors are exact pinned Tiger-source table entries selected by exact Tower state bytes. They prioritize D1 behavioral fixtures but do not independently prove that unpromoted D1 lane semantics or runtime effects are identical.',
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({
        'status':out['status'],'selected_indices':out['selected_indices'],
        'blend_rt0':[(x['index'],x['render_targets'][0] if x['render_targets'] else None) for x in tables['blend']],
        'depth_stencil':[{k:x[k] for k in ('index','depth_enable','depth_write_mask','depth_func','stencil_enable','stencil_read_mask','stencil_write_mask')} for x in tables['depth_stencil']],
        'rasterizer':tables['rasterizer'],'depth_bias':tables['depth_bias'],'violations':v,
    },indent=2))
    return 0 if out['status']=='D1_TOWER_PIPELINE_STATE_SOURCE_TABLES_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
