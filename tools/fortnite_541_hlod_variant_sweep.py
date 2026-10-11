#!/usr/bin/env python3
"""SHA1-authenticated original 5.41 HLOD UStaticMesh variant coverage audit.

Reuses the independently compiled Rust native decoder for deliberately
different source asset families. No copyrighted source bytes stored in Git.
"""
from pathlib import Path
import subprocess
import fortnite_541_r2_material_probe as r2
ROOT="FortniteGame/Content/Athena/Maps"
SAMPLES=[
("POI/HLOD/Athena_POI_Bridge_003_0_HLOD","SM_Athena_POI_Bridge_003_0_S_GeoSlope_2W_Straight_Outer#3"),
("Buildings/1x1/HLOD/Athena_REM_1x1_Shack_a_0_HLOD","SM_Athena_REM_1x1_Shack_a_0_Boardwalk_Archway#29"),
("Buildings/1x1/HLOD/Athena_REM_1x1_Shack_c_0_HLOD","SM_Athena_REM_1x1_Shack_c_0_SM_Farm_Roof1_PeakCap#6"),
("Buildings/1x1/HLOD/Athena_REM_1x1_Shack_b_0_HLOD","SM_Athena_REM_1x1_Shack_b_0_SM_Farm_Wall#11"),
("Buildings/3x3/HLOD/Athena_RUR_3x3_House_c_1_HLOD","SM_Athena_RUR_3x3_House_c_1_SM_FORT_Floors_Generic_BasicTileBeams_C#657"),
("Buildings/1x1/HLOD/Athena_SS_1x1_Outdoor3_006_0_HLOD","SM_Athena_SS_1x1_Outdoor3_006_0_Farm_Roof1_Peak3"),
("Buildings/1x1/Arid/HLOD/Athena_ARID_1x1_Shack_b_0_HLOD","SM_Athena_ARID_1x1_Shack_b_0_Farm_Roof1_Peak#6"),
("Buildings/1x1/HLOD/Athena_NP_1x1_Shack_001_0_HLOD","SM_Athena_NP_1x1_Shack_001_0_Farm_Roof1_Peak3"),
("Buildings/5x5/HLOD/Athena_SUB_5x5_House2_a_1_HLOD","SM_Athena_SUB_5x5_House2_a_1_S_FORT_Garden_End#6"),
("Buildings/3x3/HLOD/Athena_SUB_3x3_GasStation_a_1_HLOD","SM_Athena_SUB_3x3_GasStation_a_1_SM_3x3decos_Fountain_Sidewalk04#9"),
("Buildings/3x3/HLOD/Athena_REM_3x3_RangerStation_b_1_HLOD","SM_Athena_REM_3x3_RangerStation_b_1_SM_FORT_Floors_Generic_BasicTile#8"),
("Buildings/3x3/HLOD/Athena_SUB_3x3_TacoStand_a_1_HLOD","SM_Athena_SUB_3x3_TacoStand_a_1_FORT_Food_Counter_A_C#21"),
]
def run():
    entries=r2.load_index()
    path=Path("/tmp/fortnite541_mesh_sweep");path.mkdir(exist_ok=True)
    binary=Path("tools/fortnite_541_hlod_rust/target/debug/fortnite-541-hlod-source-proof")
    if not binary.is_file():raise ValueError("compile Rust HLOD proof first")
    count=0
    for i,(rel,object_name) in enumerate(SAMPLES):
        base=f"{ROOT}/{rel}"
        files=[]
        for ext in (".uasset",".uexp"):
            source=entries[base+ext]
            raw=r2.source_payload(source)
            output=path/f"sample{i}{ext}"
            output.write_bytes(raw)
            files.append(str(output))
        p=subprocess.run([str(binary),"/tmp/fortnite541_native_root.umap",
            "/tmp/fortnite541_native_root.uexp",*files,object_name],
            capture_output=True,text=True)
        if p.returncode==0:
            matching=[line for line in p.stdout.splitlines()
                if "FORTNITE_NATIVE_ORIGINAL_LOD0_GEOMETRY" in line]
            print("FORTNITE_MESH_SWEEP_PASS "+str({"path":rel,"object":object_name,
                "source":matching[0] if matching else ""}),flush=True)
            count+=1
        else:
            print("FORTNITE_MESH_SWEEP_BLOCK "+str({"path":rel,"object":object_name,
                "error":p.stderr.strip()[-600:]}),flush=True)
    print(f"FORTNITE_ORIGINAL_MESH_VARIANT_COVERAGE accepted={count} sampled={len(SAMPLES)}",flush=True)
if __name__=="__main__":run()
