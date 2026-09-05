#!/usr/bin/env python3
"""Reusable D1 ROI baked-static vertex attribute decoder.

Primary position decoding is strict: if position location is not proven, geometry
is not emitted. Secondary attributes are enrichment and fail closed without
removing otherwise-valid position/index geometry.

The D1 layouts here follow the pinned native-era reader in:
MontagueM/Charm@50d36ee1f9ecadad7522504c20b1f3f9c97e30af
Tiger/Schema/Model/VertexBuffer.cs::ReadD1VertexData.

A particularly important correction is secondary stride 0x18. For the common
D1 static pairing (primary stride != 0x0C), the first four bytes are UV and the
remaining 20 bytes have *two serialized layouts selected per vertex*:

  A: color@+0x04, normal int16x4@+0x08, tangent int16x4@+0x10
     when int16@+0x0E == 0 and int16@+0x16 == +/-32767
  B: normal int16x4@+0x04, tangent int16x4@+0x0C, color@+0x14

This replaces the older incorrect fixed ``normal@+6`` interpretation.  Tangents
and vertex colours are retained as first-class decoded attributes so shader-input
reconstruction does not silently discard material-control channels.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


def _snorm16(raw: np.ndarray) -> np.ndarray:
    x=raw.astype(np.float32)/32767.0
    return np.maximum(x,-1.0)


def _bytes2d(data:bytes,stride:int)->np.ndarray:
    if stride<=0 or len(data)%stride:
        raise ValueError(f'buffer size {len(data)} not divisible by stride {stride}')
    return np.frombuffer(data,dtype=np.uint8).reshape(len(data)//stride,stride)


def _raw_i16(data:bytes,stride:int,offset:int,ncomp:int=1)->np.ndarray:
    a=_bytes2d(data,stride)
    if offset+ncomp*2>stride:
        raise ValueError(f'attribute {offset:#x}+{ncomp*2:#x} exceeds stride {stride:#x}')
    out=np.empty((len(a),ncomp),dtype=np.int16)
    for j in range(ncomp):
        out[:,j]=np.frombuffer(a[:,offset+j*2:offset+j*2+2].copy().tobytes(),dtype='<i2')
    return out


def _vec_snorm16(data:bytes,stride:int,offset:int,ncomp:int)->np.ndarray:
    return _snorm16(_raw_i16(data,stride,offset,ncomp))


def _rgba8(data:bytes,stride:int,offset:int)->np.ndarray:
    a=_bytes2d(data,stride)
    if offset+4>stride: raise ValueError('vertex color outside stride')
    return a[:,offset:offset+4].astype(np.float32)/255.0


def _float_vec(data:bytes,stride:int,offset:int,ncomp:int)->np.ndarray:
    a=_bytes2d(data,stride)
    if offset+ncomp*4>stride:
        raise ValueError(f'float attribute {offset:#x}+{ncomp*4:#x} exceeds stride {stride:#x}')
    out=np.empty((len(a),ncomp),dtype=np.float32)
    for j in range(ncomp):
        out[:,j]=np.frombuffer(a[:,offset+j*4:offset+j*4+4].copy().tobytes(),dtype='<f4')
    return out


@dataclass
class StaticAttributes:
    positions: np.ndarray
    uv0: np.ndarray|None
    normals: np.ndarray|None
    tangents: np.ndarray|None
    colors: np.ndarray|None
    primary_stride: int
    secondary_stride: int|None
    layout: dict


def decode_static_attributes(v0:bytes,stride0:int,v1:bytes|None=None,stride1:int|None=None)->StaticAttributes:
    # Position prefix is mandatory and remains strict.
    if stride0==0x30:
        pos=_float_vec(v0,stride0,0,3)
    elif stride0 in (0x08,0x0C,0x10,0x1C,0x20):
        pos=_vec_snorm16(v0,stride0,0,3)
    else:
        raise ValueError(f'unsupported D1 static primary stride {stride0:#x}')

    uv=None;norm=None;tangent=None;color=None
    layout={'primary':{'position_offset':0,'source':'Charm ReadD1VertexData'}}

    # D1 primary layouts. Vector4 source fields are decoded to xyz for normals
    # and xyzw for tangents. Position W is source metadata and is not POSITION.W.
    if stride0 in (0x0C,0x1C,0x20):
        uv=_vec_snorm16(v0,stride0,0x08,2)
        layout['primary']['uv0_offset']=0x08
    if stride0 in (0x1C,0x20):
        norm=_vec_snorm16(v0,stride0,0x0C,3)
        tangent=_vec_snorm16(v0,stride0,0x14,4)
        layout['primary']['normal_offset']=0x0C
        layout['primary']['normal_serialized_components']=4
        layout['primary']['tangent_offset']=0x14
        layout['primary']['tangent_serialized_components']=4
    if stride0==0x20:
        # Position8 + UV4 + normal8 + tangent8 = 0x1C, then RGBA8.
        color=_rgba8(v0,stride0,0x1C)
        layout['primary']['color_offset']=0x1C
        layout['primary']['color_storage']='RGBA8_UNORM'
    if stride0==0x30:
        norm=_float_vec(v0,stride0,0x10,3)
        tangent=_float_vec(v0,stride0,0x20,4)
        layout['primary'].update({
            'position_storage':'float4','normal_offset':0x10,'normal_storage':'float4',
            'tangent_offset':0x20,'tangent_storage':'float4',
        })

    if v1 is not None:
        # Secondary attributes may be omitted if the backing/layout is invalid;
        # geometry preservation must not depend on visual enrichment.
        sec={};secondary_ok=True
        if stride1 is None or stride1<=0:
            secondary_ok=False;sec={'status':'UNDECODED','reason':'secondary payload supplied without valid stride'}
        elif len(v1)%stride1:
            secondary_ok=False;sec={'status':'UNDECODED','reason':f'secondary backing {len(v1)} not divisible by stride {stride1}'}
        elif len(v1)//stride1 != len(pos):
            secondary_ok=False;sec={'status':'UNDECODED','reason':f'primary/secondary vertex count mismatch {len(pos)} != {len(v1)//stride1}'}

        if secondary_ok:
            sec={'status':'DECODED','source':'Charm ReadD1VertexData bufferIndex=1'}
            if stride1==0x14: # 20 bytes
                if uv is None:
                    # UV4 + normal8 + tangent8.
                    uv=_vec_snorm16(v1,stride1,0,2)
                    norm=_vec_snorm16(v1,stride1,4,3)
                    tangent=_vec_snorm16(v1,stride1,0x0C,4)
                    sec.update({'uv0_offset':0,'normal_offset':4,'normal_serialized_components':4,
                                'tangent_offset':0x0C,'tangent_serialized_components':4})
                else:
                    # normal8 + tangent8 + RGBA8.
                    norm=_vec_snorm16(v1,stride1,0,3)
                    tangent=_vec_snorm16(v1,stride1,8,4)
                    color=_rgba8(v1,stride1,0x10)
                    sec.update({'normal_offset':0,'normal_serialized_components':4,
                                'tangent_offset':8,'tangent_serialized_components':4,
                                'color_offset':0x10,'color_storage':'RGBA8_UNORM'})

            elif stride1==0x10: # 16 = normal8 + tangent8
                norm=_vec_snorm16(v1,stride1,0,3)
                tangent=_vec_snorm16(v1,stride1,8,4)
                sec.update({'normal_offset':0,'normal_serialized_components':4,
                            'tangent_offset':8,'tangent_serialized_components':4})

            elif stride1==0x18: # 24, D1 conditional static layout
                if stride0==0x0C and uv is not None:
                    # Exact source branch for otherStride==0x0C and _uvExists:
                    # normal8 + tangent8 + four int16 values treated by Charm as
                    # VertexColours.  Preserve its existence/layout but withhold
                    # portable COLOR_0 because the storage is not RGBA8 and the
                    # exact normalization semantics are still unresolved.
                    norm=_vec_snorm16(v1,stride1,0,3)
                    tangent=_vec_snorm16(v1,stride1,8,4)
                    sec.update({
                        'normal_offset':0,'normal_serialized_components':4,
                        'tangent_offset':8,'tangent_serialized_components':4,
                        'source_color_offset':0x10,'source_color_storage':'int16x4',
                        'portable_color_status':'WITHHELD_PENDING_INT16_COLOR_SEMANTICS',
                    })
                else:
                    if uv is not None:
                        # ReadD1VertexData consumes UV at +0 for this branch. A
                        # second already-decoded UV channel would be ambiguous in
                        # our single-UV adapter; do not silently overwrite it.
                        sec={'status':'UNDECODED','reason':f'stride 0x18 with primary stride {stride0:#x} already supplying UV is not representable as one UV0 without guessing'}
                    else:
                        uv=_vec_snorm16(v1,stride1,0,2)
                        check=_raw_i16(v1,stride1,0x0E,1)[:,0]
                        check2=_raw_i16(v1,stride1,0x16,1)[:,0]
                        branch_a=(check==0)&((check2==32767)|(check2==-32767))

                        # Branch A: color@4, normal@8, tangent@16.
                        na=_vec_snorm16(v1,stride1,0x08,3)
                        ta=_vec_snorm16(v1,stride1,0x10,4)
                        ca=_rgba8(v1,stride1,0x04)
                        # Branch B: normal@4, tangent@12, color@20.
                        nb=_vec_snorm16(v1,stride1,0x04,3)
                        tb=_vec_snorm16(v1,stride1,0x0C,4)
                        cb=_rgba8(v1,stride1,0x14)
                        norm=np.where(branch_a[:,None],na,nb).astype(np.float32)
                        tangent=np.where(branch_a[:,None],ta,tb).astype(np.float32)
                        color=np.where(branch_a[:,None],ca,cb).astype(np.float32)
                        sec.update({
                            'uv0_offset':0,
                            'conditional_layout':True,
                            'selector':'int16@0x0E == 0 && int16@0x16 in {+32767,-32767}',
                            'branch_a':{'color_offset':0x04,'normal_offset':0x08,'tangent_offset':0x10},
                            'branch_b':{'normal_offset':0x04,'tangent_offset':0x0C,'color_offset':0x14},
                            'branch_a_vertices':int(branch_a.sum()),
                            'branch_b_vertices':int((~branch_a).sum()),
                            'normal_serialized_components':4,'tangent_serialized_components':4,
                            'color_storage':'RGBA8_UNORM',
                        })

            elif stride1==0x0C: # 12 = UV4 + normal8
                if uv is None:
                    uv=_vec_snorm16(v1,stride1,0,2);sec['uv0_offset']=0
                norm=_vec_snorm16(v1,stride1,4,3)
                sec.update({'normal_offset':4,'normal_serialized_components':4})
            else:
                sec={'status':'UNDECODED','reason':f'unsupported D1 static secondary stride {stride1:#x}'}
        layout['secondary']=sec

    for name,a in [('positions',pos),('uv0',uv),('normals',norm),('tangents',tangent),('colors',color)]:
        if a is not None and not np.isfinite(a).all(): raise ValueError(f'non-finite {name}')
    return StaticAttributes(pos,uv,norm,tangent,color,stride0,stride1,layout)
