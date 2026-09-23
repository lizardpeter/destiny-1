#!/usr/bin/env python3
"""Cluster exact D1 PS4 pixel shaders by source-closed structural signatures.

The signature deliberately uses only exact facts:
* ordered image opcode/resource/dmask/sampler usage;
* exact ImmConstBuffer API-slot+dword read sets;
* terminal MRT0 export compression/operand shape;
* per-channel terminal texture/cbuffer/unknown-register leaf shapes.

Shader hashes, native code hashes, and visible-material frequencies are retained as
members/weights but are not used to assign human material or renderer semantics.
"""
from __future__ import annotations
import argparse,collections,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def canon_image(row):
 out=[]
 for x in row.get('instructions',[]):
  out.append({
   'opcode':x.get('opcode'),
   'resources':sorted(int(q['texture_index']) for q in x.get('resources',[]) if q.get('texture_index') is not None),
   'samplers':sorted(int(q['sampler_index']) for q in x.get('samplers',[]) if q.get('sampler_index') is not None),
   'dmask':x.get('dmask_channels'),
  })
 return out

def canon_cbuf(row):
 return {str(k):[int(x) for x in v] for k,v in sorted((row.get('api_slot_read_dwords') or {}).items(),key=lambda kv:int(kv[0]))}

def canon_terminal(row):
 ch={}
 for name in ('R','G','B','A'):
  q=((row.get('channels') or {}).get(name) or {}).get('value_slice') or {}
  ch[name]={
   'disabled':bool(q.get('disabled_export_lane')),
   'cbuffer_dwords':{str(k):[int(x) for x in v] for k,v in sorted((q.get('cbuffer_dwords') or {}).items(),key=lambda kv:int(kv[0]))},
   'texture_channels':sorted((int(x['texture_index']),str(x['channel'])) for x in q.get('texture_sample_channels',[])),
   'unknown_registers':sorted(str(x) for x in q.get('unknown_registers',[])),
   'literals':sorted(str(x) for x in q.get('literals',[])),
  }
 return {
  'compressed':bool(row.get('terminal_mrt0_compressed')),
  'operand_shape':['off' if str(x).lower()=='off' else ('vreg' if str(x).startswith('v') else str(x)) for x in row.get('terminal_mrt0_operands',[])],
  'channels':ch,
 }

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--extract-report',type=Path,required=True)
 ap.add_argument('--image-usage',type=Path,required=True)
 ap.add_argument('--cbuffer-usage',type=Path,required=True)
 ap.add_argument('--terminal-mrt0',type=Path,required=True)
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 ex=json.loads(a.extract_report.read_text());im=json.loads(a.image_usage.read_text())
 cb=json.loads(a.cbuffer_usage.read_text());tm=json.loads(a.terminal_mrt0.read_text())
 v=[]
 if ex.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or ex.get('error_count'):v.append('extract report not exact')
 if im.get('status')!='D1_GCN_IMAGE_RESOURCE_USAGE_EXACT':v.append('image usage not exact')
 if cb.get('status')!='D1_GCN_CBUFFER_USAGE_EXACT' or cb.get('missing_usage'):v.append('cbuffer usage not exact')
 if tm.get('status')!='D1_GCN_TERMINAL_MRT0_DEPENDENCY_CENSUS_EXACT':v.append('terminal MRT0 census not exact')
 iby={norm(x['shader']):x for x in im.get('shaders',[])}
 cby={norm(x['shader']):x for x in cb.get('shaders',[])}
 tby={norm(x['shader']):x for x in tm.get('shaders',[])}
 members=[];groups=collections.defaultdict(list)
 for x in ex.get('shaders',[]):
  if x.get('error'):continue
  sh=norm(x['shader']);missing=[k for k,d in [('image',iby),('cbuffer',cby),('terminal',tby)] if sh not in d]
  if missing:
   v.append(f'{sh}: missing reports {missing}');continue
  sig={
   'image':canon_image(iby[sh]),
   'cbuffer':canon_cbuf(cby[sh]),
   'terminal':canon_terminal(tby[sh]),
  }
  key=json.dumps(sig,sort_keys=True,separators=(',',':'))
  row={'shader':sh,'visible_material_count':int(x.get('visible_material_count',0)),
       'native_shader':x.get('native_shader'),'gcn_sha256':x.get('gcn_sha256'),
       'gcn_bytes':int(x.get('gcn_bytes',0)),'signature':sig}
  members.append(row);groups[key].append(row)
 clusters=[]
 for n,(key,rows) in enumerate(sorted(groups.items(),key=lambda kv:(-sum(x['visible_material_count'] for x in kv[1]),-len(kv[1]),min(x['shader'] for x in kv[1]))),1):
  sig=rows[0]['signature']
  clusters.append({
   'cluster_index':n,'shader_family_count':len(rows),
   'visible_material_count_sum':sum(x['visible_material_count'] for x in rows),
   'shaders':sorted(x['shader'] for x in rows),
   'members':sorted([{k:x[k] for k in ('shader','visible_material_count','native_shader','gcn_sha256','gcn_bytes')} for x in rows],key=lambda x:(-x['visible_material_count'],x['shader'])),
   'signature':sig,
  })
 out={
  'schema':'d1_shader_structural_family_cluster/v1',
  'status':'D1_SHADER_STRUCTURAL_FAMILY_CLUSTER_EXACT' if members and not v else 'D1_SHADER_STRUCTURAL_FAMILY_CLUSTER_PARTIAL',
  'shader_family_count':len(members),'cluster_count':len(clusters),
  'visible_material_count_sum':sum(x['visible_material_count'] for x in members),
  'multi_shader_cluster_count':sum(len(x['shaders'])>1 for x in clusters),
  'clusters':clusters,'violations':v,
  'semantic_boundary':{
   'cluster_membership':'EXACT_STRUCTURAL_SIGNATURE_EQUALITY',
   'human_shader_family_meaning':'WITHHELD',
   'material_or_sky_role':'WITHHELD',
   'portable_equation_equivalence':'NOT_PROVEN_BY_SIGNATURE_EQUALITY_ALONE',
  },
  'policy':'Clusters identify identical exact resource/cbuffer/terminal dependency shapes. They prioritize reverse engineering but do not assert identical arithmetic constants, human roles, or bit-identical outputs.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'shaders':len(members),'clusters':len(clusters),
  'top_clusters':[{'n':x['cluster_index'],'weight':x['visible_material_count_sum'],'shaders':x['shaders']} for x in clusters[:20]],
  'violations':v},indent=2))
 return 0 if out['status']=='D1_SHADER_STRUCTURAL_FAMILY_CLUSTER_EXACT' else 2

if __name__=='__main__':raise SystemExit(main())
