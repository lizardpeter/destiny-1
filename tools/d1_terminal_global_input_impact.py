#!/usr/bin/env python3
"""Measure exact terminal-output impact of selected renderer-global cbuffer leaves.

Inputs are operation-preserving symbolic MRT0 reports plus exact shader-extract
weights from one or more renderer domains.  The tool never assigns engine field
names to API slots/dwords; it only proves whether an exact token survives into
terminal R/G/B/A expressions and how much source-visible material weight it covers.
"""
from __future__ import annotations
import argparse,collections,json,re
from pathlib import Path

DEFAULT_TOKENS=('API12[28]','API12[29]','API12[30]','API13[6]','API13[7]')

def pair(s):
 if '=' not in s:raise argparse.ArgumentTypeError('expected LABEL=PATH')
 k,p=s.split('=',1)
 return k,Path(p)

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

def main():
 ap=argparse.ArgumentParser()
 ap.add_argument('--extract',action='append',type=pair,required=True)
 ap.add_argument('--symbolic',action='append',type=pair,required=True)
 ap.add_argument('--token',action='append')
 ap.add_argument('--out',type=Path,required=True)
 a=ap.parse_args()
 ex=dict(a.extract);sy=dict(a.symbolic);tokens=tuple(a.token or DEFAULT_TOKENS);v=[]
 if set(ex)!=set(sy):v.append(f'domain mismatch extract={sorted(ex)} symbolic={sorted(sy)}')
 domains={};global_rows={t:{'domains':{},'family_count':0,'visible_material_weight':0,'channel_counts':collections.Counter()} for t in tokens}

 for label in sorted(set(ex)&set(sy)):
  e=json.loads(ex[label].read_text());s=json.loads(sy[label].read_text())
  if e.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or e.get('error_count'):v.append(f'{label}: extract not exact')
  if s.get('status')!='D1_GCN_TERMINAL_SYMBOLIC_REDUCER_EXACT' or s.get('violations'):v.append(f'{label}: symbolic report not exact')
  weights={norm(x['shader']):int(x.get('visible_material_count',0)) for x in e.get('shaders',[]) if not x.get('error')}
  rows={norm(x['shader']):x for x in s.get('shaders',[])}
  if set(weights)!=set(rows):v.append(f'{label}: shader set mismatch')
  tokrows={}
  for tok in tokens:
   families=[];channel_counts=collections.Counter();occ=0;weight=0
   for sh in sorted(set(weights)&set(rows)):
    r=rows[sh]
    if not r.get('exact_terminal_expression'):v.append(f'{label}:{sh}: terminal expression not exact')
    channels=[]
    for ch,expr in (r.get('terminal_expressions') or {}).items():
     n=str(expr).count(tok)
     if n:
      channels.append(ch);channel_counts[ch]+=1;occ+=n
    if channels:
     w=weights[sh];weight+=w
     families.append({'shader':sh,'visible_material_count':w,'channels':sorted(channels),
                      'expression_occurrence_count':sum(str(x).count(tok) for x in (r.get('terminal_expressions') or {}).values())})
   row={'token':tok,'shader_family_count':len(families),'visible_material_weight':weight,
        'channel_family_counts':dict(sorted(channel_counts.items())),'expression_occurrence_count':occ,
        'families':families}
   tokrows[tok]=row
   g=global_rows[tok];g['domains'][label]={'shader_family_count':len(families),'visible_material_weight':weight,
                                          'channel_family_counts':row['channel_family_counts'],'expression_occurrence_count':occ}
   g['family_count']+=len(families);g['visible_material_weight']+=weight;g['channel_counts'].update(channel_counts)
  domains[label]={'shader_family_count':len(weights),'visible_material_weight':sum(weights.values()),'tokens':tokrows}

 for tok,g in global_rows.items():g['channel_counts']=dict(sorted(g['channel_counts'].items()))
 ranked=sorted(({'token':t,**g} for t,g in global_rows.items()),
               key=lambda x:(-x['visible_material_weight'],-x['family_count'],x['token']))
 out={'schema':'d1_terminal_global_input_impact/v1',
      'status':'D1_TERMINAL_GLOBAL_INPUT_IMPACT_EXACT' if domains and not v else 'D1_TERMINAL_GLOBAL_INPUT_IMPACT_PARTIAL',
      'tokens':list(tokens),'domains':domains,'global_ranked_tokens':ranked,'violations':v,
      'semantic_boundary':{
       'terminal_token_presence':'EXACT_OPERATION_PRESERVING_SYMBOLIC_EXPRESSION',
       'visible_material_weight':'EXACT_SOURCE_CORPUS_FREQUENCY',
       'engine_field_names':'WITHHELD',
       'producer_objects':'WITHHELD',
       'live_runtime_values':'WITHHELD',
      },
      'policy':'Token impact is exact expression membership, not a semantic field identification. Repeated token text is not simplified or algebraically reassociated.'}
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'ranked':[{
  'token':x['token'],'families':x['family_count'],'visible_material_weight':x['visible_material_weight'],
  'channels':x['channel_counts'],'domains':x['domains']} for x in ranked],'violations':v},indent=2))
 return 0 if out['status']=='D1_TERMINAL_GLOBAL_INPUT_IMPACT_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
