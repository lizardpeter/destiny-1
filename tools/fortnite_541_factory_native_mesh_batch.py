#!/usr/bin/env python3
"""Find and authenticate every native LOD0 source mesh for Toilet Factory.

Source identities come from the original POI UMap or the native Blueprint CDO
decoder's exact FPackageIndex output, never guessed from filenames. Traverse
all seven original retail PAK indexes, using the same resolution order as the
production importer. Source bytes are SHA1 verified; only temporary CI cache.
"""
import collections
import json
from pathlib import Path
import re
import fortnite_541_r2_material_probe as retail
import fortnite_541_skylight_cube_probe as split
from fortnite_541_material_expression_probe import Catalog
from fortnite_541_all_poi_coverage import actor_inventory,checked_package,SPLITS,ROOT

WORLD=ROOT+"Athena/Maps/POI/Athena_POI_ToiletFactory_001"
LOG=Path("/tmp/fortnite541_cdo_output.log")
MANIFEST=Path("/tmp/fortnite541_factory_lod0.tsv")
DEST=Path("/tmp/fortnite541_factory_mesh_lods")
ORDER=("s3","s2","s1","s4","s5","chunk1","main")

def locate(package, indexes):
    path=checked_package(package,".uasset")
    if path is None:return None
    base=path[:-7]
    for archive in ORDER:
        ix=indexes[archive]
        candidates=(base,) if archive=="main" else (base.removeprefix(ROOT),base)
        for candidate in candidates:
            if candidate+".uasset" in ix and candidate+".uexp" in ix:
                return archive,candidate
    return None

def read_source(archive,key,indexes):
    if archive=="main":
        return retail.source_payload(indexes["main"][key])
    if archive=="chunk1":name="pakchunk1-WindowsClient.pak"
    else:name=f"pakchunk0_{archive}-WindowsClient.pak"
    sha=dict(SPLITS)[archive]
    split.URL=("https://r2.houseofkublai.com/Fortnite/5.41/"
               "FortniteGame/Content/Paks/"+name)
    split.INDEX_SHA=sha
    return split.payload(indexes[archive][key])

def run():
    main=retail.load_index()
    cat=Catalog(retail.source_payload(main[WORLD+".umap"]),
                retail.source_payload(main[WORLD+".uexp"]))
    total,direct,inherited,errors=actor_inventory(cat)
    if total!=1335 or len(direct)!=186:
        raise ValueError(f"Factory source actor counts changed: {total} {len(direct)}")
    # Original cooked direct mesh identities are counted once PER placed actor.
    instances=collections.Counter(identity for identity,_ in direct)
    # Native CDO proof output is an authoritative source mesh identity with
    # its actual original placed Blueprint actor multiplicity.
    cdo_rows=0
    for line in LOG.read_text(encoding="utf-8").splitlines():
        if not line.startswith("FORTNITE_FACTORY_CDO_MESH "):
            continue
        match=re.search(r'actors=(\d+) source=("(?:\\.|[^"\\])*")',line)
        if not match:
            raise ValueError("native CDO source row format changed: "+line)
        n=int(match.group(1))
        identity=json.loads(match.group(2))
        instances[identity]+=n
        cdo_rows+=1
    expected=sum(instances.values())
    if expected!=1332:
        raise ValueError(f"Native class CDO source identities missing: {expected}/1332")
    indexes={"main":main}
    for archive,sha in SPLITS:
        name=("pakchunk1-WindowsClient.pak" if archive=="chunk1"
              else f"pakchunk0_{archive}-WindowsClient.pak")
        split.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/"+name
        split.INDEX_SHA=sha
        indexes[archive]=split.source()
    # Cache by original package (many separate UObject mesh names can share it).
    packages=collections.defaultdict(list)
    for identity,n in instances.items():
        packages[identity.split("::")[0]].append((identity,n))
    DEST.mkdir(parents=True,exist_ok=True)
    manifest=[]
    sources=collections.Counter()
    unavailable=[]
    for i,(package,meshes) in enumerate(sorted(packages.items())):
        location=locate(package,indexes)
        target=DEST/str(i)
        if location:
            archive,key=location
            for ext in (".uasset",".uexp"):
                (DEST/(str(i)+ext)).write_bytes(read_source(
                    archive,key+ext,indexes
                ))
            sources[archive]+=1
        else:
            unavailable.append(package)
        for identity,n in meshes:
            manifest.append(f"{identity}\t{n}\t{target if location else ''}")
    MANIFEST.write_text("\n".join(manifest)+"\n",encoding="utf-8")
    print("FORTNITE_FACTORY_LOD0_SOURCE_PREP "+json.dumps({
        "source_actors":total,"native_cdo_classes_resolved":cdo_rows,
        "mesh_referenced_actors":expected,
        "unique_mesh_object_identities":len(instances),
        "unique_source_mesh_packages":len(packages),
        "source_archives":dict(sources),
        "unavailable_original_packages":unavailable,
        "manifest":str(MANIFEST)
    },sort_keys=True),flush=True)
if __name__=="__main__":
    run()
