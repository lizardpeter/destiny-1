#!/usr/bin/env python3
"""Find exact original Fortnite 5.41 Arid/Road/Gravel albedo source archives.

Source identities come from UMaterialFunctions referenced by
M_Athena_Terrain_Master and source LandscapeLayerInfo. Only SHA1-verified
original PAK directory entries qualify; never substitute a lookalike name.
"""
import json
from fortnite_541_all_poi_coverage import SPLITS,ROOT
import fortnite_541_r2_material_probe as retail
import fortnite_541_skylight_cube_probe as split

CANDIDATES={
 "Gravel":"/Game/Packages/DS_Fortnight/WhiteRockCustom_D::WhiteRockCustom_D",
 "Road":"/Game/Packages/DS_Fortnight/SM/Textures/T_Street_Road_D::T_Street_Road_D",
 "Arid":"/Game/Environments/Sets/Arid/Textures/T_desert_sand_base_C::T_desert_sand_base_C",
}
def main():
    indexes={"main":retail.load_index()}
    for chunk,sha in SPLITS:
        pak="pakchunk1-WindowsClient.pak" if chunk=="chunk1" else f"pakchunk0_{chunk}-WindowsClient.pak"
        split.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/"+pak
        split.INDEX_SHA=sha
        indexes[chunk]=split.source()
    count=0
    for paint,source in CANDIDATES.items():
        pkg=source.split("::")[0].removeprefix("/Game/")
        matched=[]
        for archive,index in indexes.items():
            prefixes=[ROOT+pkg,pkg] if archive!="main" else [ROOT+pkg]
            for prefix in set(prefixes):
                found=[{"ext":ext,"source_bytes":index[prefix+ext][2],
                        "encrypted":bool(index[prefix+ext][5]),
                        "compressed":index[prefix+ext][3]!=0}
                       for ext in (".uasset",".uexp",".ubulk")
                       if prefix+ext in index]
                if found:matched.append({"archive":archive,"base":prefix,"files":found})
        pair=[m for m in matched if any(f["ext"]==".uasset" for f in m["files"]) and
              any(f["ext"]==".uexp" for f in m["files"])]
        print("ATHENA_541_RETAIL_PAINT_TEXTURE_PAK "+json.dumps({
            "layer":paint,"source_identity":source,"packages":matched,
            "original_source_pair_locations":len(pair)
        },sort_keys=True),flush=True)
        count+=len(pair)
    print("ATHENA_541_RETAIL_SPLIT_PAINT_TEXTURE_SUMMARY "+
          json.dumps({"candidate_textures":len(CANDIDATES),
                      "verified_archive_pairs":count},sort_keys=True),flush=True)
if __name__=="__main__":main()
