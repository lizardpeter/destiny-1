#!/usr/bin/env python3
"""Source-prove the exact cube/LOD semantic frontier used by D1 PS 808EE505.

This is intentionally supplemental to the generic VOP/MIMG proof. It closes only the
operations and address-profile facts needed by instructions 342..399, using immutable
AMD/GPU ISA sources plus the exact source-owned D1 resource inventory. No visual role
for texture 5 is inferred.
"""
from __future__ import annotations
import argparse, hashlib, json, traceback
from pathlib import Path


def sha(p: Path) -> str:
    return hashlib.sha256(p.read_bytes()).hexdigest()


def main() -> int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--ir',type=Path,required=True)
    ap.add_argument('--texture-roles',type=Path,required=True)
    ap.add_argument('--vop1-source',type=Path,required=True)
    ap.add_argument('--vop2-source',type=Path,required=True)
    ap.add_argument('--vop3-source',type=Path,required=True)
    ap.add_argument('--modifier-syntax',type=Path,required=True)
    ap.add_argument('--intrinsics-source',type=Path,required=True)
    ap.add_argument('--gem5-revision',required=True)
    ap.add_argument('--llvm-revision',required=True)
    ap.add_argument('--modifier-revision',required=True)
    ap.add_argument('-o','--output',type=Path,required=True)
    a=ap.parse_args();viol=[];payload={}
    try:
        ir=json.load(open(a.ir));tr=json.load(open(a.texture_roles))
        assert ir['status']=='D1_GCN_STRUCTURAL_IR_COMPLETE' and int(ir.get('schema_version',0))>=2
        assert ir['shader']=='808EE505' and ir['instruction_count']==456
        assert tr['status']=='D1_WORLD_TEXTURE_ROLE_INVENTORY_EVIDENCE_SCOPED'
        assert tr['source_status']=='D1_WORLD_VISIBLE_MATERIAL_TEXTURE_EXPORT'
        m=tr['materials']['80D777B6'];assert m['pixel_shader']=='808EE505'
        b={int(x['texture_index']):x for x in m['bindings']}
        t5=b[5]
        assert t5['texture']=='80AAFB08'
        assert t5['resource_class']=='CUBEMAP'
        assert t5['shape']==[256,256,6]
        assert t5['format_name']=='BC1'

        v1=a.vop1_source.read_text(errors='replace')
        v2=a.vop2_source.read_text(errors='replace')
        v3=a.vop3_source.read_text(errors='replace')
        mod=a.modifier_syntax.read_text(errors='replace')
        intr=a.intrinsics_source.read_text(errors='replace')

        sqrt='// D.f = sqrt(S0.f).'
        subrev='// D.f = S1.f - S0.f.'
        madlegacy='// D.f = S0.f * S1.f + S2.f (DX9 rules, 0.0 * x = 0.0).'
        cubema='// D.f = 2.0 * cubemap major axis. XYZ coordinate is given in (S0.f, S1.f,'
        cubetc='// D.f = cubemap T coordinate. XYZ coordinate is given in (S0.f, S1.f,'
        cubesc='// D.f = cubemap S coordinate. XYZ coordinate is given in (S0.f, S1.f,'
        cubeid='// D.f = cubemap face ID ({0.0, 1.0, ..., 5.0}). XYZ coordinate is given in'
        assert sqrt in v1 and 'Inst_VOP1__V_SQRT_F32::execute' in v1
        assert subrev in v2 and 'Inst_VOP2__V_SUBREV_F32::execute' in v2
        assert madlegacy in v3 and 'Inst_VOP3__V_MAD_LEGACY_F32::execute' in v3
        for lit,cls in [
            (cubema,'Inst_VOP3__V_CUBEMA_F32::execute'),
            (cubetc,'Inst_VOP3__V_CUBETC_F32::execute'),
            (cubesc,'Inst_VOP3__V_CUBESC_F32::execute'),
            (cubeid,'Inst_VOP3__V_CUBEID_F32::execute')]:
            assert lit in v3 and cls in v3,(lit,cls)

        assert 'Computes the absolute value of its operand.' in mod
        assert 'abs(<operand>)                           Get the absolute value of a floating-point operand.' in mod
        assert 'Computes the negative value of its operand.' in mod
        assert 'neg(<operand>)     Get the negative value of a floating-point operand.' in mod
        assert '-<operand>         The same as above (an SP3 syntax).' in mod
        assert 'mul:2                                    Multiply the result by 2.' in mod
        assert 'output modifiers are applied before' in mod
        assert 'clamping' in mod

        cube_dim='def AMDGPUDimCube : AMDGPUDimProps<0x3, "cube", "CUBE", ["s", "t"], ["face"]>;'
        assert cube_dim in intr
        assert '// Name of the {lod} or {clamp} argument that is appended to the coordinates,' in intr
        assert 'let LodOrClamp = "lod" in' in intr
        assert 'AMDGPUSampleHelper_Compare<"_L", "_l", []>' in intr
        assert 'list<AMDGPUArg> CoordSliceArgs =' in intr
        assert 'makeArgList<!listconcat(coord_names, slice_names), llvm_anyfloat_ty>.ret;' in intr
        assert '!listconcat(!if(IsSample, dim.CoordSliceArgs, dim.CoordSliceIntArgs),' in intr
        assert '[AMDGPUArg<LLVMMatchType<0>, LodClampMip>]' in intr
        assert 'defm int_amdgcn_image_getlod' in intr
        assert 'AMDGPUImageDimSampleDims<"GET_LOD", AMDGPUSample, 1>' in intr

        ins=ir['instructions']
        expected={
          348:('v_add_f32',['v18','-v18','1.0 clamp']),
          350:('v_sqrt_f32',['v18','v18']),
          369:('v_max_f32',['v10','v8','v8 mul:2']),
          375:('v_mad_legacy_f32',['v12','-v5','v6','v12']),
          376:('v_mad_legacy_f32',['v14','-v4','v6','v14']),
          377:('v_mad_legacy_f32',['v10','-v3','v6','v10']),
          378:('v_cubema_f32',['v3','v12','v14','v10']),
          379:('v_cubetc_f32',['v4','v12','v14','v10']),
          380:('v_cubesc_f32',['v5','v12','v14','v10']),
          381:('v_rcp_f32',['v3','abs(v3)']),
          383:('v_cubeid_f32',['v18','v12','v14','v10']),
          384:('v_mad_legacy_f32',['v17','v4','v3','s12']),
          385:('v_mad_legacy_f32',['v16','v5','v3','s12']),
          387:('image_get_lod',['v5','v[16:19]','s[4:11]','s[0:3] dmask:2']),
          395:('v_subrev_f32',['v12','s15','v12']),
          399:('image_sample_l',['v[3:6]','v[16:19]','s[4:11]','s[0:3] dmask:15']),
        }
        for i,(op,ops) in expected.items():
            x=ins[i];assert x['opcode']==op and x['operands']==ops,(i,x['opcode'],x['operands'])
        for i,opcode,dmask,channels in [(387,'image_get_lod',2,'y'),(399,'image_sample_l',15,'xyzw')]:
            im=ins[i]['image'];assert im['opcode']==opcode and im['dmask']==dmask and im['dmask_channels']==channels
            assert im['textures']==[5] and im['samplers']==[6]
            rp=im['resource_provenance'];sp=im['sampler_provenance']
            assert len(rp)==1 and rp[0]['texture_index']==5 and rp[0]['sgpr']=='s[4:11]'
            assert len(sp)==1 and sp[0]['sampler_index']==6 and sp[0]['sgpr']=='s[0:3]'

        semantics={
          'v_sqrt_f32':{'operation':'SQRT','equation':'D = sqrt(S0)','source_literal':sqrt},
          'v_subrev_f32':{'operation':'SUBREV','equation':'D = S1 - S0','source_literal':subrev},
          'v_mad_legacy_f32':{'operation':'LEGACY_MAD_DX9','equation':'D = legacy_mul_dx9(S0,S1) + S2','zero_rule':'0.0*x = 0.0','source_literal':madlegacy},
          'v_cubema_f32':{'operation':'CUBE_MAJOR_AXIS_X2','equation':'D = 2.0 * cubemap_major_axis(S0,S1,S2)','source_literal':cubema},
          'v_cubetc_f32':{'operation':'CUBE_T','equation':'D = cubemap_T(S0,S1,S2)','source_literal':cubetc},
          'v_cubesc_f32':{'operation':'CUBE_S','equation':'D = cubemap_S(S0,S1,S2)','source_literal':cubesc},
          'v_cubeid_f32':{'operation':'CUBE_FACE_ID','equation':'D = cubemap_face_id_0_to_5(S0,S1,S2)','source_literal':cubeid},
          'abs_modifier':{'operation':'ABS','equation':'S = abs(S)','application_order':'before neg if present'},
          'neg_modifier':{'operation':'NEG','equation':'S = -S','application_order':'after abs if present'},
          'mul2_output_modifier':{'operation':'OUTPUT_MUL2','equation':'D = D * 2.0','application_order':'before clamp'},
        }
        for q in semantics.values():
            q['gem5_revision']=a.gem5_revision if q['operation'] not in ('ABS','NEG','OUTPUT_MUL2') else None
            q['modifier_revision']=a.modifier_revision if q['operation'] in ('ABS','NEG','OUTPUT_MUL2') else None

        payload={
          'shader':'808EE505','material':'80D777B6',
          'texture5':{'texture':'80AAFB08','resource_class':'CUBEMAP','shape':[256,256,6],'format_name':'BC1'},
          'value_semantics':semantics,
          'cube_address_profile':{
            'llvm_revision':a.llvm_revision,
            'dimension':'CUBE',
            'logical_coordinate_order':['s','t','face'],
            'image_get_lod_387':{
              'native_vaddr':['v16','v17','v18','v19'],
              'source_closed_logical_args':{'s':'v16','t':'v17','face':'v18'},
              'v19_meaning':'WITHHELD_NATIVE_EXTRA_LANE',
              'texture_index':5,'sampler_index':6,'dmask':'y'
            },
            'image_sample_l_399':{
              'native_vaddr':['v16','v17','v18','v19'],
              'source_closed_logical_args':{'s':'v16','t':'v17','face':'v18','lod':'v19'},
              'lod_position_basis':'LLVM _L LodOrClamp is appended after cube CoordSliceArgs',
              'texture_index':5,'sampler_index':6,'dmask':'xyzw'
            }
          },
          'source_files':{
            'vop1_sha256':sha(a.vop1_source),'vop2_sha256':sha(a.vop2_source),'vop3_sha256':sha(a.vop3_source),
            'modifier_sha256':sha(a.modifier_syntax),'intrinsics_sha256':sha(a.intrinsics_source)
          },
          'semantic_boundary':{
            'texture5_dimension':'EXACT_SOURCE_OWNED_RESOURCE_CLASS',
            'cube_coordinate_profile':'EXACT_LLVM_SOURCE_PROFILE',
            'sample_l_explicit_lod_lane':'EXACT_LLVM_SOURCE_PROFILE',
            'get_lod_fourth_native_lane':'WITHHELD',
            'texture5_visual_material_role':'WITHHELD',
            'portable_cubemap_shader_reconstruction':'WITHHELD'
          }
        }
    except Exception:
        viol.append(traceback.format_exc())
    out={'schema_version':1,'status':'D1_GCN_CUBE_LOD_SEMANTICS_SOURCE_PROVEN' if payload and not viol else 'D1_GCN_CUBE_LOD_SEMANTICS_PARTIAL','proof':payload,'violations':viol,'policy':'Only immutable ISA semantics, exact source-owned resource dimension, and exact target instruction bindings are promoted. Texture visual role and the extra native GET_LOD vaddr lane remain withheld.'}
    a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(json.dumps(out,indent=2)+'\n');print(json.dumps(out,indent=2));return 0 if not viol else 2
if __name__=='__main__':raise SystemExit(main())
