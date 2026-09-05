#!/usr/bin/env python3
"""Reusable D1 ROI baked-static vertex attribute decoder.

The layouts here are the layouts independently exercised by the D1 branch of
MontevenDynamicExtractor for Static meshes. Position/UV/normal components are
signed normalized int16 divided by 32767. This module keeps layout selection
explicit and fail-closed so unsupported strides do not silently manufacture UVs.
"""
from __future__ import annotations
from dataclasses import dataclass
import numpy as np


def _snorm16(raw: np.ndarray) -> np.ndarray:
    x=raw.astype(np.float32)/32767.0
    return np.maximum(x,-1.0)


def _vec_snorm16(data:bytes,stride:int,offset:int,ncomp:int)->np.ndarray:
    if stride<=0 or len(data)%stride:
        raise ValueError(f'buffer size {len(data)} not divisible by stride {stride}')
    n=len(data)//stride
    if offset+ncomp*2>stride:
        raise ValueError(f'attribute {offset:#x}+{ncomp*2:#x} exceeds stride {stride:#x}')
    a=np.frombuffer(data,dtype=np.uint8).reshape(n,stride)
    # Copy because the strided byte view is not naturally aligned for int16.
    raw=np.empty((n,ncomp),dtype=np.int16)
    for j in range(ncomp):
        raw[:,j]=np.frombuffer(a[:,offset+j*2:offset+j*2+2].copy().tobytes(),dtype='<i2')
    return _snorm16(raw)


def _rgba8(data:bytes,stride:int,offset:int)->np.ndarray:
    if stride<=0 or len(data)%stride: raise ValueError('bad stride')
    n=len(data)//stride
    if offset+4>stride: raise ValueError('vertex color outside stride')
    a=np.frombuffer(data,dtype=np.uint8).reshape(n,stride)
    return a[:,offset:offset+4].astype(np.float32)/255.0


@dataclass
class StaticAttributes:
    positions: np.ndarray
    uv0: np.ndarray|None
    normals: np.ndarray|None
    colors: np.ndarray|None
    primary_stride: int
    secondary_stride: int|None
    layout: dict


def decode_static_attributes(v0:bytes,stride0:int,v1:bytes|None=None,stride1:int|None=None)->StaticAttributes:
    # Common D1 static primary position prefix.
    if stride0==0x30:
        n=len(v0)//stride0
        f=np.frombuffer(v0,dtype='<f4').reshape(n,stride0//4)
        pos=f[:,:3].astype(np.float32)
    elif stride0 in (0x08,0x0C,0x10,0x1C,0x20):
        pos=_vec_snorm16(v0,stride0,0,3)
    else:
        raise ValueError(f'unsupported D1 static primary stride {stride0:#x}')

    uv=None;norm=None;color=None
    layout={'primary':{'position_offset':0}}

    # Source-crosschecked D1 Static primary layouts.
    if stride0 in (0x0C,0x1C,0x20):
        uv=_vec_snorm16(v0,stride0,0x08,2)
        layout['primary']['uv0_offset']=0x08
    if stride0==0x1C:
        norm=_vec_snorm16(v0,stride0,0x0C,3)
        layout['primary']['normal_offset']=0x0C
    if stride0==0x20:
        color=_rgba8(v0,stride0,0x1A)
        layout['primary']['color_offset']=0x1A

    if v1 is not None:
        if stride1 is None: raise ValueError('secondary payload supplied without stride')
        if len(v1)%stride1: raise ValueError('secondary backing not stride-aligned')
        if len(v1)//stride1 != len(pos):
            raise ValueError(f'primary/secondary vertex count mismatch {len(pos)} != {len(v1)//stride1}')
        sec={}
        # Source-crosschecked D1 Static secondary layouts.
        if stride1==0x14: # 20
            if uv is None:
                uv=_vec_snorm16(v1,stride1,0,2); sec['uv0_offset']=0
                norm=_vec_snorm16(v1,stride1,4,3); sec['normal_offset']=4
            else:
                norm=_vec_snorm16(v1,stride1,0,3); sec['normal_offset']=0
                color=_rgba8(v1,stride1,0x10); sec['color_offset']=0x10
        elif stride1==0x10: # 16
            norm=_vec_snorm16(v1,stride1,0,3); sec['normal_offset']=0
        elif stride1==0x18: # 24
            if uv is None:
                uv=_vec_snorm16(v1,stride1,0,2); sec['uv0_offset']=0
            # D1 source reads normal from +6 for this specific static layout.
            norm=_vec_snorm16(v1,stride1,6,3); sec['normal_offset']=6
        elif stride1==0x0C: # 12
            if uv is None:
                uv=_vec_snorm16(v1,stride1,0,2); sec['uv0_offset']=0
            norm=_vec_snorm16(v1,stride1,4,3); sec['normal_offset']=4
        else:
            raise ValueError(f'unsupported D1 static secondary stride {stride1:#x}')
        layout['secondary']=sec

    for name,a in [('positions',pos),('uv0',uv),('normals',norm),('colors',color)]:
        if a is not None and not np.isfinite(a).all(): raise ValueError(f'non-finite {name}')
    return StaticAttributes(pos,uv,norm,color,stride0,stride1,layout)
