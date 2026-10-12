#!/usr/bin/env python3
"""Prove missing Fortnite 5.41 POI Blueprint CDOs in split PAKs.

These seven exact UBlueprintGeneratedClass source identities and actor
multiplicities come from all 40 retail source POI UMaps. They are omitted
by the game importer's main-Pak-only Blueprint preparation.
Source bytes are SHA1 verified by the original 5.41 archive readers.
"""
import json
from pathlib import Path
import fortnite_541_skylight_cube_probe as source
from fortnite_541_all_poi_coverage import SPLITS,checked_package,ROOT
SOURCES=[
    (5,"/Game/Environments/Sets/Super_V_Lair/Props/BP/SVLair_Banner_01::SVLair_Banner_01_C","s3"),
    (2,"/Game/Environments/Sets/Super_V_Lair/Props/BP/SVLair_Holotable_Side::SVLair_Holotable_Side_C","s3"),
    (2,"/Game/Environments/Sets/Super_V_Lair/Props/BP/SVLair_Holotable::SVLair_Holotable_C","s3"),
    (1,"/Game/Environments/Props/MovieSet/BP/Movie_Set_Camera::Movie_Set_Camera_C","s2"),
    (18,"/Game/Packages/Fortress_Transylvania/Test_Assets/Blueprints/ArtificialLights/BP_TRV_ALight_Torch_02::BP_TRV_ALight_Torch_02_C","s4"),
    (8,"/Game/Missions/Quests/ReactiveQuests/Events/Anniversary2018/Props/Athena_PartyBalloons::Athena_PartyBalloons_C","s3"),
    (2,"/Game/Packages/DS_Fortnite_Terrain_NoLOD/Blueprints/BP_Waterfall::BP_Waterfall_C","s3"),
]
ROOT_DIR=Path("/tmp/fortnite541_split_only_cdos")
MANIFEST=Path("/tmp/fortnite541_split_only_cdos.tsv")
def run():
    ROOT_DIR.mkdir(parents=True,exist_ok=True)
    by_archive={}
    rows=[]; verified=0
    for archive,sha in SPLITS:
        entries=[(n,cls) for n,cls,split in SOURCES if split==archive]
        if not entries:continue
        pak="pakchunk1-WindowsClient.pak" if archive=="chunk1" else f"pakchunk0_{archive}-WindowsClient.pak"
        source.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/"+pak
        source.INDEX_SHA=sha
        ix=source.source()
        for n,cls in entries:
            package=checked_package(cls,".uasset")
            if package is None:raise ValueError(f"original class package path malformed: {cls}")
            base=package[:-7]
            matches=[name for name in (base.removeprefix(ROOT),base)
                     if name+".uasset" in ix and name+".uexp" in ix]
            if len(matches)!=1:
                raise ValueError(f"original CDO {cls} split {archive}: {len(matches)} source mounts")
            target=ROOT_DIR/str(len(rows))
            for ext in (".uasset",".uexp"):
                payload=source.payload(ix[matches[0]+ext])
                target.with_suffix(ext).write_bytes(payload)
                verified+=1
            rows.append((n,cls,str(target),archive))
            by_archive[archive]=by_archive.get(archive,0)+1
    MANIFEST.write_text("".join(f"{cls}\t{n}\t{stem}\n"
                       for n,cls,stem,_ in rows),encoding="utf-8")
    result={"source_class_packages":len(rows),
            "source_placed_actors":sum(r[0] for r in rows),
            "authentic_source_files":verified,
            "source_archives":by_archive,
            "manifest":str(MANIFEST),
            "source_classes":[{"name":cls,"actors":n,"pak":archive}
                              for n,cls,_,archive in rows]}
    print("FORTNITE_SPLIT_ONLY_BLUEPRINT_CDO_SOURCE "+json.dumps(result,sort_keys=True),flush=True)
    if len(rows)!=7 or result["source_placed_actors"]!=38 or verified!=14:
        raise ValueError("original seven split CDO source classes changed")
if __name__=="__main__":run()
