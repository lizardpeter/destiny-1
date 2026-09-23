#!/usr/bin/env python3
"""Exact symbolic closure for ten one-material Tower sky tail families.

Rows are accepted only when source material scope, retail shader identity, terminal
export address, and operation-preserving symbolic expression hashes all match the
pinned corpus. Human sky/pass semantics remain withheld.
"""
from __future__ import annotations
import argparse,json
from pathlib import Path

def norm(x):return str(x).upper().removeprefix('0X').zfill(8)

CFG={
'80B9EA14':(1,'80B9EA2F','ae18d406d3f988402d1376a61499389a96cacf5f3842e3b6dd164182bcdf8157','3aa4e3742e99689ae40ee9c01eccae17a7f62f82cc6544f57f43f5e5562bb24d',436,'0000000001A8',[0,1,2],
 {'R':'5fbadd14dbf5ba99f570c881cf93380e7e76c19d793dd629138c66becfee290c','G':'6b1c0db2b4026852b6d4a2df6504f22ac85668da61b09ee0f19a7452e8802b3a','B':'bd2700230c50ae666bd008c36b53256858c909ec0d34e16bd502b73667f9e0cd','A':'227961830e782ba7c3dd3ce3657577c79c148b30b6bb7180be25838c9296f77c'}),
'80B9EA16':(1,'80B9EA31','b823313e21e2da2410abd7b6bb75139a51c7ad11d4ec7b4e5a7eb63fa1011478','f04ca7cf4de65112039e67ba481c52582cde9a7254ef64fcfef3854865ad9942',372,'000000000168',[0,1,2],
 {'R':'f8182aad51e2349a504e897fcb91565bf261432d70f8171ebdf320d4cc073b45','G':'21116d48cf8c6022bdc149eaccdf453eb81cf545074cd56996cfddecc4bf2f50','B':'5dd96e5c2f9501fc4fb263c8dd78fbc07ff412b64fde43df8d8d4e91d01e6aca','A':'bc2c6eb13c56ac11ded18dc4562d007b4b5e63ae8a342af8f267dcf6ae2686c8'}),
'80B9EA1C':(1,'80B9EA49','fecac41a13bad2a7c3832f93935c200b82e6ed6bdec3dc7f4ce2110cfa45fb92','6b74aa5672e3db9d5add56c06421f16cc3de52d82760255daeb0ea45db35e2e5',636,'000000000270',[0,1,2],
 {'R':'201add4161967699922eb6489c90f1cc4ec20a17fbc5e12fb9ad931e624c91fb','G':'671e57d8f12d8fc36f9dfe17ba561c5fe8dc0930151d117182204fa406a75a94','B':'d55e7e9d5d62dd504f13c5207f7ab1496c5d8cec10186e247f4cdc1b5bf3dec3','A':'8696cb0a03b3f827f0598c7c8f6b81497af4373fd3931716b7b88b968b5734fc'}),
'80B9EA1D':(1,'80B9EA4A','91b7884573ec729f112cdf38a85cec61e9f42b4b050b1d27ee40f758985a6176','36dad4c10ce2e7be69e6a77476dbc4d7b2dd4a9061e52fea0f494b1f9ae125c7',476,'0000000001D0',[0,1,2],
 {'R':'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9','G':'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9','B':'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9','A':'b219b000cf6a82a91a099cf1b80c3ee4b4f8443bf0a9050ee7361e04133e031f'}),
'80B9EA24':(1,'80B9EA3D','a277366e552597151974f6c0e83176da6054eb87b1fd54d783f549977300e55e','ff90e8827bef3a32f7b9d510d9ec125207d69ab9df8773f27b38feffd8384a1d',228,'0000000000D8',[0,1,2],
 {'R':'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9','G':'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9','B':'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9','A':'5289a7dae513ce169513aa82c1eec68d33188153f16828e937f6beb21deb7120'}),
'80B9EA26':(1,'80B9EA3F','c9a02003c71004e3da9f342de9cb30b2bcadcab14fcd0cd06c763cd9d5186410','e572eea8ef081d9745a7d812dd2deb3168af62203587ca0a0f5048e9e8dd20d1',292,'000000000118',[0,1,2],
 {'R':'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9','G':'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9','B':'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9','A':'4103bc16b5e28a22393b02b46316d9dafb036265fe2eb7d06866db1502e4f4ac'}),
'80B9EA2B':(1,'80B9EA44','15504ab31c8391b3686e1ef6d4f210dde638bc7d279393eee78b7a5a1f205195','61df0cd09dccbfd897daef6917bd96f1cdcd1e194ec9c63ab915bd7a431acbed',376,'00000000016C',[0,1,2],
 {'R':'2be142b47bb03d231da797f98ff9890b598b4cbbe051f83709f8fdbfd44b6249','G':'f9a2d44d264b866b2592b347316a105781129491c000a43c89b8ed642eef313e','B':'b9c0348e31b52827ad6c806ec3fe090120d4a62875b10b5816cc138daf9b268e','A':'98c5bab409c88f353fcc86527f775bef5b75795fca941c974fc7c9626c2c2651'}),
'80B9F728':(1,'80B9F741','0f9128f08612a7d4e74d8a5728dddd77f43b038883c437541b7b2e3132ec99c7','6966bcc7a3dace73cf34d3ccd700447604fa15bf0e45c9fbf97c42af3b8b6f32',376,'00000000016C',[0,1,2],
 {'R':'f8182aad51e2349a504e897fcb91565bf261432d70f8171ebdf320d4cc073b45','G':'21116d48cf8c6022bdc149eaccdf453eb81cf545074cd56996cfddecc4bf2f50','B':'5dd96e5c2f9501fc4fb263c8dd78fbc07ff412b64fde43df8d8d4e91d01e6aca','A':'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9'}),
'80B9F775':(1,'80AA99A3','399d50f6e6d4d73d542892e22c487a4efa1c56b8693a562f5f252addec4598af','418b9878983aa495fdca7af8fba2c8e1beff0a6fc107c9093596340a536956d3',284,'000000000110',[0],
 {'R':'44058a257d5c331491aca7a5580bfbad3eae0c187e9e115b5fe055587f06ca53','G':'5e9a2eecaccb8b8695f66492ca16e99d665e9d4e2b62d67fe55e7d7ab961322a','B':'426e8ba70b3c7464a6b2f9efa9afa1b139259ec9d4a30cf2bb1dbc685a05d322','A':'5feceb66ffc86f38d952786c6d696c79c2dbc239dd4e91b46729d73a27fb57e9'}),
'80B9FC88':(1,'80B9FC8C','7e0d4dc35c7cf98ec94237aedf985edaa1988d5a348fd706d7f70977ad51f25a','4d0109ea7730aee774c0a668baccafa896ef2c83fa78cfbca1453cfb4ee6d913',304,'000000000124',[0],
 {'R':'2aeaadbdd7995459f7f7aa50f600aad6df7017a2e9047119eb2fb1ec6ee49276','G':'a1a389a1cd6b237eb2d6603174be85eeb53966b02b1f24167fad58abc17f363d','B':'845452894ca5f00264b0cb0df3e561d4ad8a7268a67833589d7849108376e431','A':'d7609b621ca70ca50814ad2a92100c69479e756ef35cc4eebbcf77f379f52b19'}),
}

def main():
 ap=argparse.ArgumentParser()
 for n in ('material-manifest','shader-report','symbolic','out'):ap.add_argument('--'+n,type=Path,required=True)
 a=ap.parse_args()
 m=json.loads(a.material_manifest.read_text());sr=json.loads(a.shader_report.read_text());sy=json.loads(a.symbolic.read_text())
 v=[];rows=[]
 if m.get('status')!='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT' or m.get('material_decode_errors') or m.get('texture_errors'):v.append('manifest not exact')
 if sr.get('status')!='D1_WORLD_PIXEL_SHADER_GCN_EXACT' or sr.get('error_count'):v.append('shader report not exact')
 if sy.get('status')!='D1_GCN_TERMINAL_SYMBOLIC_REDUCER_EXACT' or sy.get('violations'):v.append('symbolic reducer input not exact')
 sby={norm(x['shader']):x for x in sr.get('shaders',[])};yby={norm(x['shader']):x for x in sy.get('shaders',[])}
 freq={norm(k):int(x) for k,x in (m.get('pixel_shader_frequency') or {}).items()};mats=m.get('materials') or {}
 for sh,cfg in CFG.items():
  freq0,native,nsha,gsha,gbytes,terminal,bindings,exprsha=cfg;errs=[]
  if freq.get(sh)!=freq0:errs.append(f'frequency {freq.get(sh)} != {freq0}')
  mm=[x for x in mats.values() if norm(x.get('pixel_shader'))==sh]
  if len(mm)!=freq0:errs.append(f'material row count {len(mm)} != {freq0}')
  for x in mm:
   inds=sorted(int(q['texture_index']) for q in (x.get('bindings') or []) if q.get('stage')=='ps')
   if inds!=bindings:errs.append(f"material {x.get('material')} binding indices {inds} != {bindings}")
  s=sby.get(sh)
  if not s:errs.append('shader row missing')
  else:
   for k,z in [('native_shader',native),('native_sha256',nsha),('gcn_sha256',gsha),('gcn_bytes',gbytes)]:
    if s.get(k)!=z:errs.append(f'{k} drift {s.get(k)!r} != {z!r}')
  y=yby.get(sh)
  if not y:errs.append('symbolic row missing')
  else:
   if y.get('terminal_mrt0_export_address')!=terminal:errs.append('terminal address drift')
   if not y.get('exact_terminal_expression'):errs.append('terminal expression not exact')
   if y.get('terminal_expression_sha256')!=exprsha:errs.append(f"expression SHA drift {y.get('terminal_expression_sha256')}")
   if y.get('unsupported_operations'):errs.append(f"unsupported operations {y['unsupported_operations']}")
   if any(y.get('terminal_unresolved_markers',{}).values()):errs.append(f"unresolved markers {y['terminal_unresolved_markers']}")
  rows.append({'shader':sh,'visible_material_count':freq0,'gcn_sha256':gsha,
               'terminal_expression_sha256':exprsha,
               'exact_terminal_equation':None if not y else y.get('terminal_expressions'),'violations':errs})
  v.extend(f'{sh}: {e}' for e in errs)
 out={
  'schema':'d1_tower_sky_symbolic_tail_proof/v1',
  'status':'D1_TOWER_SKY_SYMBOLIC_TAIL_PROOF_EXACT' if len(rows)==10 and not v else 'D1_TOWER_SKY_SYMBOLIC_TAIL_PROOF_PARTIAL',
  'shader_family_count':len(rows),'visible_material_count':sum(x['visible_material_count'] for x in rows),
  'visible_material_fraction':sum(x['visible_material_count'] for x in rows)/74,
  'rows':rows,'violations':v,
  'semantic_boundary':{
   'terminal_expression':'EXACT_NATIVE_OPERATION_ORDER',
   'human_sky_semantics':'WITHHELD',
   'runtime_producer_identity':'WITHHELD',
   'portable_renderer_equivalence':'NOT_IMPLIED',
  },
  'policy':'Each terminal expression is accepted only by pinned retail identity and exact operation-preserving expression hash. No human role is inferred.',
 }
 a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
 print(json.dumps({'status':out['status'],'families':len(rows),'materials':out['visible_material_count'],
                   'rows':[{'shader':x['shader'],'sha':x['terminal_expression_sha256'],'violations':x['violations']} for x in rows],
                   'violations':v},indent=2))
 return 0 if out['status']=='D1_TOWER_SKY_SYMBOLIC_TAIL_PROOF_EXACT' else 2
if __name__=='__main__':raise SystemExit(main())
