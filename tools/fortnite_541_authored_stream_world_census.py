#!/usr/bin/env python3
"""Find all 16 Fortnite 5.41 authored Athena root streamed UWorlds in retail PAKs.

The game currently reports 8 cached and 8 missing streamed maps. Recover
the root ULevelStreaming WorldAsset paths, compare real SHA1 verified PAK
indexes across all known mounts, never invent a world or non-source map.
"""
import json,struct
import fortnite_541_r2_material_probe as main
import fortnite_541_skylight_cube_probe as split
from fortnite_541_material_expression_probe import Catalog
from fortnite_541_all_poi_coverage import SPLITS,ROOT

def run():
    ix=main.load_index()
    base=ROOT+"Athena/Maps/Athena_Terrain"
    cat=Catalog(main.source_payload(ix[base+".umap"]),
                main.source_payload(ix[base+".uexp"]))
    worlds=[]
    for i,ex in enumerate(cat.exports,1):
        if cat.class_name(ex) not in ("LevelStreamingAlwaysLoaded","LevelStreamingDynamic"):
            continue
        fields,_=cat.props(cat.export_data(ex))
        entry=[f for f in fields if f[0]=="WorldAsset"]
        if len(entry)!=1 or entry[0][1]!="SoftObjectProperty":
            raise ValueError("original Athena WorldAsset source fields invalid")
        raw=entry[0][3]
        if len(raw)!=12:raise ValueError("original WorldAsset FSoftObjectPath not 12 bytes")
        idx,instance,subpath=struct.unpack("<IIi",raw)
        if instance or subpath or idx>=len(cat.names):raise ValueError("original WorldAsset source name malformed")
        asset=cat.names[idx]
        if not asset.startswith("/Game/") or "." not in asset:
            raise ValueError("original WorldAsset not rooted at retail /Game")
        package,obj=asset.removeprefix("/Game/").rsplit(".",1)
        if obj!=package.rsplit("/",1)[-1]:raise ValueError("source WorldAsset object mismatch")
        worlds.append({"asset":asset,"source_path":"FortniteGame/Content/"+package,
                       "stream_class":cat.class_name(ex),"original_source":cat.path(i)})
    archives={"main":ix}
    for chunk,sha in SPLITS:
        name="pakchunk1-WindowsClient.pak" if chunk=="chunk1" else f"pakchunk0_{chunk}-WindowsClient.pak"
        split.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/"+name
        split.INDEX_SHA=sha
        archives[chunk]=split.source()
    census=[]
    for world in worlds:
        package=world["source_path"]
        found=[]
        for archive,index in archives.items():
            variants=(package,) if archive=="main" else (package,package.removeprefix(ROOT))
            for key in variants:
                if key+".umap" in index and key+".uexp" in index:
                    found.append({"archive":archive,"source_package":key})
        census.append({**world,"authenticated_source_pairs":found})
    # Inspect genuine source world exports for authored light/fog components
    # and non-landscape scene objects before admitting them to the renderer.
    from collections import Counter
    for world in census:
        key=world["source_path"]
        if any(z in key for z in ("/Landscape/","Athena_Streaming_Grid")):
            continue
        umap=ix.get(key+".umap");uexp=ix.get(key+".uexp")
        if umap is None or uexp is None:continue
        cat=Catalog(main.source_payload(umap),main.source_payload(uexp))
        counter=Counter(cat.class_name(ex) for ex in cat.exports)
        candidates=[]
        for i,ex in enumerate(cat.exports,1):
            kind=cat.class_name(ex)
            if any(z in kind.lower() for z in ("light","fog","sky","sun","timeofday",
                                               "foliage","staticmesh","atmosphere")):
                candidates.append({"class":kind,"object":cat.path(i)})
        print("FORTNITE_541_AUTHENTIC_STREAM_SCENE_CONTENTS "+json.dumps({
            "world":world["asset"],"source_exports":len(cat.exports),
            "class_census":counter.most_common(30),
            "original_render_lighting_candidates":candidates[:100],
            "all_candidates_count":len(candidates),
        },sort_keys=True),flush=True)
    print("FORTNITE_AUTHORED_ROOT_WORLD_ARCHIVE_CENSUS "+json.dumps({
        "root":base,"source_stream_count":len(worlds),
        "available_streams":sum(bool(w["authenticated_source_pairs"]) for w in census),
        "unavailable_streams":sum(not bool(w["authenticated_source_pairs"]) for w in census),
        "worlds":census,
    },sort_keys=True),flush=True)
if __name__=="__main__":run()
