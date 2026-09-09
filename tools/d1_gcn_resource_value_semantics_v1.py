#!/usr/bin/env python3
"""Source-backed architectural registry for the exact D1 GFX7 resource/LDS value surface.

This is deliberately below shader/material meaning.  It records the GFX7 operand domains and
result boundaries of every observed IMAGE, BUFFER/TBUFFER and DS VGPR-producing instruction.
Actual image/buffer descriptor contents, bound D1 material resources, memory contents and
texture-role semantics are separate provenance gates.
"""
from __future__ import annotations
import json

import d1_gcn_vector_value_semantics_v1 as frontier

SCHEMA = "d1_gcn_resource_value_semantics/v1"
STATUS = "D1_GCN_RESOURCE_VALUE_SEMANTICS_SOURCE_CLOSED"
AMD = {
    "vendor": "Advanced Micro Devices, Inc.",
    "title": "AMD Sea Islands Series Instruction Set Architecture",
    "document_id": "70653",
    "revision": "1.3",
    "release_date": "2013-12-01",
    "architecture": "GCN 2 / GFX7 / Sea Islands",
    "official_url": "https://docs.amd.com/v/u/en-US/sea-islands-instruction-set-architecture_0",
}

IMAGE_WITH_SAMPLER = {
    "image_gather4_lz", "image_gather4_lz_o", "image_get_lod",
    "image_sample", "image_sample_d", "image_sample_l", "image_sample_lz", "image_sample_lz_o",
}
IMAGE_WITHOUT_SAMPLER = {"image_get_resinfo", "image_load_mip"}
IMAGE_OPS = IMAGE_WITH_SAMPLER | IMAGE_WITHOUT_SAMPLER
BUFFER_OPS = {"buffer_load_dword", "tbuffer_load_format_xyz", "tbuffer_load_format_xyzw"}
DS_MEMORY_OPS = {"ds_read2_b32", "ds_read_b32"}
DS_NON_MEMORY_OPS = {"ds_swizzle_b32"}
DS_OPS = DS_MEMORY_OPS | DS_NON_MEMORY_OPS
OPS = IMAGE_OPS | BUFFER_OPS | DS_OPS


def source(locator: str) -> dict:
    return {**AMD, "locator": locator}


def behavior(op: str) -> dict:
    if op in IMAGE_OPS:
        return {
            "domain": "IMAGE",
            "resource_descriptor_sgpr_dwords": 8,
            "sampler_descriptor_sgpr_dwords": 4 if op in IMAGE_WITH_SAMPLER else 0,
            "vgpr_address_or_coordinate_input": True,
            "result_semantics": "GFX7_IMAGE_OPERATION_RESULT",
            "result_value_status": "RESOURCE_CONTENT_OPAQUE",
            "descriptor_value_status": "EXACT_REGISTER_STATE_IDENTITY_CONTENTS_NOT_YET_BOUND",
            "source": source("Image Instructions / MIMG encoding: VADDR + 8-dword SRSRC and sampler-bearing forms add 4-dword SSAMP"),
        }
    if op in BUFFER_OPS:
        return {
            "domain": "BUFFER",
            "resource_descriptor_sgpr_dwords": 4,
            "vgpr_address_or_index_input": True,
            "result_semantics": "GFX7_BUFFER_OPERATION_RESULT",
            "result_value_status": "RESOURCE_CONTENT_OPAQUE",
            "descriptor_value_status": "EXACT_REGISTER_STATE_IDENTITY_CONTENTS_NOT_YET_BOUND",
            "source": source("Buffer/Typed Buffer Instructions: 4-dword buffer resource descriptor plus vector address/index and optional scalar offset"),
        }
    if op in DS_MEMORY_OPS:
        return {
            "domain": "DS_LDS_MEMORY",
            "resource_descriptor_sgpr_dwords": 0,
            "vgpr_address_input": True,
            "implicit_m0": "LDS_SIZE_CLAMP",
            "result_semantics": "GFX7_LDS_READ_RESULT",
            "result_value_status": "LDS_CONTENT_OPAQUE",
            "source": source("Data Share / LDS access: vector address, encoded offsets and implicit M0 LDS size/clamp state"),
        }
    if op in DS_NON_MEMORY_OPS:
        return {
            "domain": "DS_SWIZZLE",
            "resource_descriptor_sgpr_dwords": 0,
            "vgpr_data_input": True,
            "implicit_m0": None,
            "result_semantics": "GFX7_DS_SWIZZLE_RESULT",
            "result_value_status": "SOURCE_CLOSED_SWIZZLE_OPERATION_VALUE_NOT_HOST_EVALUATED",
            "source": source("DS_SWIZZLE_B32: cross-lane swizzle operation; no LDS memory-bank access"),
        }
    raise KeyError(op)


def validate() -> list[str]:
    bad=[]
    if IMAGE_OPS != set(frontier.IMAGE_VALUE_OPAQUE):
        bad.append(f"image_surface:{sorted(IMAGE_OPS)}!={sorted(frontier.IMAGE_VALUE_OPAQUE)}")
    if BUFFER_OPS != set(frontier.BUFFER_VALUE_OPAQUE):
        bad.append(f"buffer_surface:{sorted(BUFFER_OPS)}!={sorted(frontier.BUFFER_VALUE_OPAQUE)}")
    if DS_OPS != set(frontier.DS_VALUE_OPAQUE):
        bad.append(f"ds_surface:{sorted(DS_OPS)}!={sorted(frontier.DS_VALUE_OPAQUE)}")
    if len(IMAGE_OPS)!=10: bad.append(f"image_opcode_count:{len(IMAGE_OPS)}!=10")
    if len(BUFFER_OPS)!=3: bad.append(f"buffer_opcode_count:{len(BUFFER_OPS)}!=3")
    if len(DS_OPS)!=3: bad.append(f"ds_opcode_count:{len(DS_OPS)}!=3")
    return bad


def document() -> dict:
    return {
        "schema":SCHEMA,
        "status":STATUS if not validate() else "INVALID",
        "source":AMD,
        "opcode_count":len(OPS),
        "image_opcodes":sorted(IMAGE_OPS),
        "buffer_opcodes":sorted(BUFFER_OPS),
        "ds_opcodes":sorted(DS_OPS),
        "opcode_behaviors":{op:behavior(op) for op in sorted(OPS)},
        "violations":validate(),
        "semantic_boundary":{
            "operand_domain_layout":"SOURCE_CLOSED",
            "register_state_identity":"NEXT_BINDING_GATE",
            "descriptor_contents":"WITHHELD",
            "runtime_resource_assignment":"WITHHELD",
            "memory_or_texture_contents":"WITHHELD",
            "shader_expression_semantics":"WITHHELD",
            "material_semantics":"WITHHELD",
            "shader_expression_semantic_promotions":0,
        },
        "policy":"Promote only ISA-defined resource/LDS operand domains and operation identities. D1 resource-table slots, material textures, constants and runtime/default resources remain separate evidence-bound provenance work.",
    }

if __name__=="__main__":
    d=document(); print(json.dumps(d,indent=2,sort_keys=True)); raise SystemExit(0 if not d["violations"] else 2)
