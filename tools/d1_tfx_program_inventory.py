#!/usr/bin/env python3
"""Inventory/disassemble preserved D1 TFX bytecode without evaluating unknown semantics.

Primary input is ``d1_world_map_lighting_census.py`` output. Opcode identities and
operand widths are independently transcribed from the pinned Charm TFX bytecode schema.
The tool records constant references, extern references, output slots and complete raw
operands. It does *not* claim which light output slot means colour/intensity/range.

For constant-indexing opcodes, both Buffer1 and Buffer2 candidate Vec4 values are shown.
This deliberately avoids assuming which D1 BufferData array is the constant bank before
retail program dataflow proves it.
"""
from __future__ import annotations

import argparse
import hashlib
import json
from collections import Counter, defaultdict
from pathlib import Path

PINNED_SOURCE = (
    'MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af '
    'Tiger/Schema/Shaders/TFX Bytecode/OpCodes.cs + Externs.cs'
)

OP_NAMES = {
    0x01:'Add',0x02:'Subtract',0x03:'Multiply',0x04:'Divide',0x05:'Multiply2',0x06:'Add2',
    0x07:'IsZero',0x08:'Min',0x09:'Max',0x0A:'LessThan',0x0B:'Dot',0x0C:'Merge_1_3',
    0x0D:'Merge_2_2',0x0E:'Unk0e',0x0F:'Unk0f',0x10:'Lerp',0x11:'Unk11',
    0x12:'MultiplyAdd',0x13:'Clamp',0x15:'Abs',0x16:'Sign',0x17:'Floor',0x18:'Ceil',
    0x19:'Round',0x1A:'Frac',0x1B:'Unk1b',0x1C:'Unk1c',0x1D:'Negate',0x1E:'VecRotSin',
    0x1F:'VecRotCos',0x20:'VecRotSinCos',0x21:'PermuteAllX',0x22:'Permute',0x23:'Saturate',
    0x25:'Unk25',0x26:'Unk26',0x27:'Triangle',0x28:'Jitter',0x29:'Wander',0x2A:'Rand',
    0x2B:'RandSmooth',0x2C:'Unk2c',0x2D:'Unk2d',0x2E:'TransformVec4',
    0x34:'PushConstantVec4',0x35:'LerpConstant',0x37:'Spline4Const',0x38:'Unk38',
    0x39:'Unk39',0x3A:'Unk3a',0x3B:'UnkLoadConstant',0x3C:'PushExternInputFloat',
    0x3D:'PushExternInputVec4',0x3E:'PushExternInputMat4',0x3F:'PushExternInputU64',
    0x40:'PushExternInputU32',0x41:'PushExternInputU64Unknown',0x42:'Unk42',
    0x43:'PushFromOutput',0x44:'PopOutput',0x45:'PopOutputMat4',0x46:'PushTemp',0x47:'PopTemp',
    0x48:'Unk48',0x49:'Unk49',0x4A:'Unk4a',0x4B:'Unk4b',0x4C:'Unk4c',
    0x4D:'PushObjectChannelVector',0x4E:'Unk4e',0x4F:'Unk4f',0x50:'Unk50',0x51:'Unk51',
    0x52:'Unk52',0x53:'Unk53',0x54:'Unk54',0x55:'Unk55',0x56:'Unk56',0x57:'Unk57',0x58:'Unk58',
}

OPERAND_LENGTH = {
    0x22:1,0x34:1,0x35:1,0x37:1,0x38:1,0x39:1,0x3A:1,0x3B:1,
    0x3C:2,0x3D:2,0x3E:2,0x3F:2,0x40:2,0x41:2,
    0x43:1,0x44:1,0x45:1,0x46:1,0x47:1,0x48:1,0x49:1,0x4A:1,0x4B:1,0x4C:1,0x4D:1,
    0x4E:4,0x4F:1,0x50:1,0x52:2,0x53:2,0x54:2,
}

EXTERNS = {
    0:'None',1:'Frame',2:'View',3:'Deferred',4:'DeferredLight',5:'DeferredUberLight',
    6:'DeferredShadow',7:'Atmosphere',8:'RigidModel',9:'EditorMesh',10:'EditorMeshMaterial',
    11:'EditorDecal',12:'EditorTerrain',13:'EditorTerrainPatch',14:'EditorTerrainDebug',
    15:'SimpleGeometry',16:'UiFont',17:'CuiView',18:'CuiObject',19:'CuiBitmap',20:'CuiVideo',
    21:'CuiStandard',22:'CuiHud',23:'CuiScreenspaceBoxes',24:'TextureVisualizer',25:'Generic',
    26:'Particle',27:'ParticleDebug',28:'GearDyeVisualizationMode',29:'ScreenArea',30:'Mlaa',
    31:'Msaa',32:'Hdao',33:'DownsampleTextureGeneric',34:'DownsampleDepth',35:'Ssao',
    36:'VolumetricObscurance',37:'Postprocess',38:'TextureSet',39:'Transparent',40:'Vignette',
    41:'GlobalLighting',42:'ShadowMask',43:'ObjectEffect',44:'Decal',45:'DecalSetTransform',
    46:'DynamicDecal',47:'DecoratorWind',48:'TextureCameraLighting',49:'VolumeFog',50:'Fxaa',
    51:'Smaa',52:'Letterbox',53:'DepthOfField',54:'PostprocessInitialDownsample',55:'CopyDepth',
    56:'DisplacementMotionBlur',57:'DebugShader',58:'MinmaxDepth',59:'SdsmBiasAndScale',
    60:'SdsmBiasAndScaleTextures',61:'ComputeShadowMapData',62:'ComputeLocalLightShadowMapData',
    63:'BilateralUpsample',64:'HealthOverlay',65:'LightProbeDominantLight',66:'LightProbeLightInstance',
    67:'Water',68:'LensFlare',69:'ScreenShader',70:'Scaler',71:'GammaControl',72:'SpeedtreePlacements',
    73:'Reticle',74:'Distortion',75:'WaterDebug',76:'ScreenAreaInput',77:'WaterDepthPrepass',
    78:'OverheadVisibilityMap',79:'ParticleCompute',80:'CubemapFiltering',81:'ParticleFastpath',
    82:'VolumetricsPass',83:'TemporalReprojection',84:'FxaaCompute',85:'VbCopyCompute',86:'UberDepth',
    87:'GearDye',88:'Cubemaps',89:'ShadowBlendWithPrevious',90:'DebugShadingOutput',91:'Ssao3d',
    92:'WaterDisplacement',93:'PatternBlending',94:'UiHdrTransform',95:'PlayerCenteredCascadedGrid',
    96:'SoftDeform',
}


def candidate(arr, idx):
    return arr[idx] if 0 <= idx < len(arr) else None


def disassemble(raw: bytes, buffer1: list, buffer2: list) -> dict:
    rows=[]; pos=0; unknown=[]; truncated=False
    while pos < len(raw):
        start=pos; op=raw[pos]; pos+=1
        name=OP_NAMES.get(op)
        if name is None:
            rows.append({'offset':start,'opcode':f'{op:02X}','name':f'UNKNOWN_{op:02X}','known':False,'raw_hex':f'{op:02X}'})
            unknown.append({'offset':start,'opcode':f'{op:02X}'})
            # Unknown operand width would desynchronise the remainder; fail closed.
            break
        n=OPERAND_LENGTH.get(op,0)
        if pos+n>len(raw):
            rows.append({'offset':start,'opcode':f'{op:02X}','name':name,'known':True,
                         'error':'truncated_operands','available':len(raw)-pos,'required':n})
            truncated=True
            break
        args=list(raw[pos:pos+n]); pos+=n
        row={'offset':start,'opcode':f'{op:02X}','name':name,'known':True,'operand_bytes':args,
             'raw_hex':raw[start:pos].hex().upper()}
        if op==0x22 and args:
            fields=args[0]; dims='xyzw'
            row['permute']='.'+''.join(dims[(fields>>shift)&3] for shift in (6,4,2,0))
        if op in (0x34,0x3B) and args:
            idx=args[0];row['constant_index']=idx
            row['buffer1_candidate']=candidate(buffer1,idx);row['buffer2_candidate']=candidate(buffer2,idx)
        if op==0x35 and args:
            idx=args[0];row['constant_start']=idx
            row['buffer1_candidates']=[candidate(buffer1,idx),candidate(buffer1,idx+1)]
            row['buffer2_candidates']=[candidate(buffer2,idx),candidate(buffer2,idx+1)]
        if op in range(0x3C,0x42) and len(args)==2:
            row['extern_id']=args[0];row['extern_name']=EXTERNS.get(args[0],f'UNKNOWN_EXTERN_{args[0]}')
            row['extern_element']=args[1]
        if op in (0x43,0x44,0x45,0x46,0x47) and args:
            row['slot_or_element']=args[0]
        rows.append(row)
    return {
        'complete': pos==len(raw) and not unknown and not truncated,
        'bytes_consumed':pos,'bytecode_bytes':len(raw),'unknown_opcodes':unknown,
        'truncated':truncated,'ops':rows,
    }


def main()->int:
    ap=argparse.ArgumentParser()
    ap.add_argument('--lighting-census',type=Path,required=True)
    ap.add_argument('--out',type=Path,required=True)
    a=ap.parse_args()
    src=json.loads(a.lighting_census.read_text())
    buffers=src.get('light_buffers',[])
    rows=[];op_hist=Counter();extern_hist=Counter();output_slots=Counter();const_refs=Counter();violations=[]
    by_program=defaultdict(list)
    for b in buffers:
        raw=bytes.fromhex(b.get('bytecode_hex',''))
        d=disassemble(raw,b.get('buffer1',[]),b.get('buffer2',[]))
        for op in d['ops']:
            op_hist[op['name']]+=1
            if 'extern_name' in op: extern_hist[op['extern_name']]+=1
            if op['name'] in ('PopOutput','PopOutputMat4') and op.get('operand_bytes'):
                output_slots[str(op['operand_bytes'][0])]+=1
            if 'constant_index' in op: const_refs[str(op['constant_index'])]+=1
            if 'constant_start' in op: const_refs[str(op['constant_start'])]+=1
        if not d['complete']:
            violations.append(f"{b.get('hash')}:disassembly_incomplete")
        program_sha=b.get('bytecode_sha256') or hashlib.sha256(raw).hexdigest()
        row={'buffer_hash':b.get('hash'),'program_sha256':program_sha,
             'buffer1_count':len(b.get('buffer1',[])),'buffer2_count':len(b.get('buffer2',[])),**d}
        rows.append(row);by_program[program_sha].append(b.get('hash'))
    groups=[{'program_sha256':k,'buffer_count':len(v),'buffer_hashes':sorted(v)} for k,v in sorted(by_program.items())]
    out={
        'schema_version':1,
        'status':'D1_TFX_PROGRAM_INVENTORY_COMPLETE' if not violations else 'D1_TFX_PROGRAM_INVENTORY_PARTIAL',
        'pinned_source':PINNED_SOURCE,
        'source_lighting_status':src.get('status'),
        'buffer_count':len(buffers),'unique_program_count':len(groups),
        'opcode_histogram':dict(op_hist),'extern_histogram':dict(extern_hist),
        'output_slot_histogram':dict(output_slots),'constant_reference_histogram':dict(const_refs),
        'program_groups':groups,'buffers':rows,'violations':violations,
        'semantic_withholding':'Opcode framing is source-pinned. Output-slot meaning and Buffer1/Buffer2 semantic roles remain unassigned until retail dataflow proves them.'
    }
    a.out.parent.mkdir(parents=True,exist_ok=True);a.out.write_text(json.dumps(out,indent=2)+'\n')
    print(json.dumps({k:out[k] for k in ('status','buffer_count','unique_program_count','opcode_histogram','extern_histogram','output_slot_histogram','constant_reference_histogram','violations')},indent=2))
    return 0 if not violations else 2

if __name__=='__main__': raise SystemExit(main())
