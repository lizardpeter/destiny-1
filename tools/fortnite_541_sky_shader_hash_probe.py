#!/usr/bin/env python3
"""Search original SkyDome cooked packages for exact SM5 compiled shader identities.

This does not infer which shader is used from filenames. Original Fortnite
PCD3D_SM5 archive index contains 96,496 exact 20-byte code hashes. Read
only the authenticated index and source SkyDome UAsset/UExp payloads.
"""
import json
import fortnite_541_r2_material_probe as main
import fortnite_541_skylight_cube_probe as s4
from fortnite_541_material_shader_link_probe import original_library_ids,hit_scan

S4="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_s4-WindowsClient.pak"
SHA="96a67f9eae257051576e368fdb61a6fb78b2f56a"
BASES=(
    "Packages/Fortress_Sky/SkyDome/Master/M_SkyDome",
    "Packages/Fortress_Sky/SkyDome/MaterialInstances/SkyDomeBasic01/Morn_M_SkyDome_Inst_Basic01",
    "Packages/Fortress_Sky/SkyDome/MaterialInstances/SkyDomeBasic01/Day_M_SkyDome_Inst_Basic01",
    "Packages/Fortress_Sky/Fortnite_SkyTwistFunction",
)
def main_run():
    lib=original_library_ids(main.load_index())
    s4.URL=S4;s4.INDEX_SHA=SHA
    contents=s4.source()
    results=[]
    for source in BASES:
        item={"material":source,"files":[]}
        for ext in (".uasset",".uexp"):
            key=source+ext
            if key not in contents:
                item["files"].append({"path":key,"absent":True})
                continue
            raw=s4.payload(contents[key])
            hits=hit_scan(raw,lib)
            item["files"].append({
                "path":key,"source_len":len(raw),
                "matched_shader_hash_count":len(hits),
                "exact_hash_locations":hits[:100],
            })
        results.append(item)
        print("FORTNITE_AUTHENTIC_SKY_SM5_SHADER_LINK "+json.dumps(item,sort_keys=True),flush=True)
    print("FORTNITE_AUTHENTIC_SKY_SM5_SHADER_LINK_SUMMARY "+json.dumps({
        "source_compiled_sm5_hashes":len(lib),
        "sky_source_package_count":len(results),
        "matched_code_hashes":sum(f.get("matched_shader_hash_count",0)
            for item in results for f in item["files"]),
    },sort_keys=True),flush=True)
if __name__=="__main__":
    main_run()
