#!/usr/bin/env python3
"""Recover logical MIMG address words hidden by pre-GFX10 disassembly.

For pre-GFX10 MIMG, the machine encoding names a starting VGPR while the number
of logical address words depends on the bound image dimension. LLVM therefore
notes that its disassembler defaults to the smallest register class. This pass
widens an address only when exact D1 binding evidence proves the dimension and
immutable AMDGPU definitions prove the argument ordering.

The first promoted case is 2D IMAGE_SAMPLE_D: ds/dh, dt/dh, ds/dv, dt/dv, s, t.
No visual texture role is inferred.
"""
from __future__ import annotations
import argparse, json, re
from pathlib import Path

VRANGE = re.compile(r"^v\[(\d+):(\d+)\]$")
VONE = re.compile(r"^v(\d+)$")


def norm(x) -> str:
    return str(x).upper().removeprefix("0X").zfill(8)


def main() -> int:
    ap = argparse.ArgumentParser()
    ap.add_argument("--ir", type=Path, required=True)
    ap.add_argument("--texture-roles", type=Path, required=True)
    ap.add_argument("--intrinsics-source", type=Path, required=True)
    ap.add_argument("--mimg-source", type=Path, required=True)
    ap.add_argument("--intrinsics-revision", required=True)
    ap.add_argument("--mimg-revision", required=True)
    ap.add_argument("-o", "--output", type=Path, required=True)
    a = ap.parse_args()

    ir = json.load(open(a.ir))
    roles = json.load(open(a.texture_roles))
    intr = a.intrinsics_source.read_text()
    mimg = a.mimg_source.read_text()
    violations = []
    rows = []
    material_name = None

    try:
        assert ir["status"] == "D1_GCN_STRUCTURAL_IR_COMPLETE"
        shader = norm(ir["shader"])
        inv = roles["shader_inventory"][shader]
        mats = inv["materials"]
        assert len(mats) == 1, (shader, mats)
        material_name = mats[0]
        mat = roles["materials"][material_name]
        bindings = {int(b["texture_index"]): b for b in mat["bindings"]}

        # Immutable LLVM source facts used by the reconstruction.
        assert (
            'def AMDGPUDim2D : AMDGPUDimProps<0x1, "2d", "2D", ["s", "t"], []>;'
            in intr
        )
        assert '!foreach(name, coord_names, "d" # name # "dh")' in intr
        assert '!foreach(name, coord_names, "d" # name # "dv")' in intr
        assert "arglistconcat<[ExtraAddrArgs," in intr
        assert "!if(Gradients, dim.GradientArgs, [])" in intr
        assert "dim.CoordSliceArgs" in intr
        assert "The disassembler defaults to the" in mimg
        assert "smallest register class." in mimg

        for x in ir["instructions"]:
            if x["opcode"] != "image_sample_d" or "image" not in x:
                continue
            image = x["image"]
            textures = image.get("textures", [])
            samplers = image.get("samplers", [])
            if len(textures) != 1 or len(samplers) != 1:
                continue
            binding = bindings.get(int(textures[0]))
            if not binding:
                continue
            resource_class = binding.get("resource_class", "")
            if not resource_class.endswith("_2D"):
                continue

            vaddr = x["operands"][1]
            rm = VRANGE.match(vaddr)
            om = VONE.match(vaddr)
            if rm:
                start = int(rm.group(1))
                nominal_end = int(rm.group(2))
            elif om:
                start = nominal_end = int(om.group(1))
            else:
                raise ValueError(f'{x["index"]}: unsupported vaddr {vaddr}')

            # LLVM AMDGPUDim2D has s,t coordinates. GradientArgs are generated
            # as all dh components followed by all dv components, and AddrArgs
            # places GradientArgs before CoordSliceArgs for sample_d.
            names = ["ds_dh", "dt_dh", "ds_dv", "dt_dv", "s", "t"]
            regs = [f"v{i}" for i in range(start, start + len(names))]
            rows.append(
                {
                    "instruction": x["index"],
                    "address": x["address_hex"],
                    "opcode": x["opcode"],
                    "texture_index": int(textures[0]),
                    "sampler_index": int(samplers[0]),
                    "texture": binding["texture"],
                    "resource_class": resource_class,
                    "shape": binding["shape"],
                    "nominal_disassembly_vaddr": vaddr,
                    "nominal_disassembly_start_vgpr": start,
                    "nominal_disassembly_end_vgpr": nominal_end,
                    "effective_dimension": "2D",
                    "effective_address_word_count": 6,
                    "effective_address_registers": regs,
                    "effective_address_components": [
                        {"register": r, "component": n}
                        for r, n in zip(regs, names)
                    ],
                    "source_basis": {
                        "dimension_source": "exact texture binding/resource class",
                        "gradient_order": (
                            "LLVM AMDGPUDimProps GradientArgs: horizontal components "
                            "then vertical components"
                        ),
                        "address_order": (
                            "LLVM AddrArgs: ExtraAddrArgs, GradientArgs, CoordSliceArgs"
                        ),
                        "disassembler_note": (
                            "LLVM MIMG disassembler defaults to smallest register class"
                        ),
                    },
                    "resolution": "EXACT_DIMENSION_AWARE_MIMG_ADDRESS",
                }
            )

        assert rows, "no exact 2D image_sample_d rows found"
    except Exception as exc:
        violations.append(repr(exc))

    out = {
        "schema_version": 1,
        "status": (
            "D1_GCN_MIMG_ADDRESS_PROVENANCE_EXACT"
            if rows and not violations
            else "D1_GCN_MIMG_ADDRESS_PROVENANCE_PARTIAL"
        ),
        "shader": ir.get("shader"),
        "material": material_name,
        "rows": rows,
        "violations": violations,
        "source_revisions": {
            "llvm_intrinsics": a.intrinsics_revision,
            "llvm_mimg": a.mimg_revision,
        },
        "policy": (
            "Effective MIMG address spans are widened beyond nominal disassembly "
            "only when the exact bound texture dimension and immutable AMDGPU "
            "address-argument ordering jointly prove the extra words. No dimension "
            "is guessed from opcode or register adjacency."
        ),
    }
    a.output.parent.mkdir(parents=True, exist_ok=True)
    a.output.write_text(json.dumps(out, indent=2) + "\n")
    print(json.dumps(out, indent=2))
    return 0 if not violations else 2


if __name__ == "__main__":
    raise SystemExit(main())
