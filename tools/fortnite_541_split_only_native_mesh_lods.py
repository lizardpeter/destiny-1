#!/usr/bin/env python3
"""Stage exact original LOD0 sources for newly resolved split-only CDO meshes."""
import collections,json,re
from pathlib import Path
from fortnite_541_factory_native_mesh_batch import locate,read_source
from fortnite_541_all_poi_coverage import SPLITS
import fortnite_541_r2_material_probe as retail
import fortnite_541_skylight_cube_probe as split

LOG=Path("/tmp/fortnite541_split_only_mesh_cdo.log")
ROOT=Path("/tmp/fortnite541_split_only_meshes")
MANIFEST=Path("/tmp/fortnite541_split_only_mesh_lods.tsv")
def run():
    groups=collections.Counter()
    for line in LOG.read_text().splitlines():
        if not line.startswith("FORTNITE_FACTORY_CDO_MESH "):
            continue
        parsed=re.search(r'actors=(\d+) source=("(?:\\.|[^"\\])*")',line)
        if not parsed:raise ValueError("original native source CDO mesh output changed")
        groups[json.loads(parsed.group(2))]+=int(parsed.group(1))
    if len(groups)!=6 or sum(groups.values())!=36:
        raise ValueError(f"authentic split CDO geometry census differs: {groups}")
    indexes={"main":retail.load_index()}
    for archive,sha in SPLITS:
        pak="pakchunk1-WindowsClient.pak" if archive=="chunk1" else f"pakchunk0_{archive}-WindowsClient.pak"
        split.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/"+pak
        split.INDEX_SHA=sha
        indexes[archive]=split.source()
    ROOT.mkdir(parents=True,exist_ok=True)
    rows=[]
    archives=collections.Counter()
    for i,(identity,n) in enumerate(sorted(groups.items())):
        pkg=identity.split("::")[0]
        loc=locate(pkg,indexes)
        if loc is None:raise ValueError(f"no authenticated source mesh LOD for {identity}")
        archive,base=loc
        target=ROOT/str(i)
        for ext in (".uasset",".uexp"):
            target.with_suffix(ext).write_bytes(read_source(archive,base+ext,indexes))
        rows.append((identity,n,str(target),archive))
        archives[archive]+=1
    MANIFEST.write_text("".join(f"{identity}\t{n}\t{base}\n" for identity,n,base,_ in rows))
    print("FORTNITE_SPLIT_ONLY_NATIVE_MESH_SOURCE "+json.dumps({
        "source_identities":len(rows),"placed_original_actors":sum(x[1] for x in rows),
        "source_authored_mesh_files":len(rows)*2,"source_archives":dict(archives),
        "meshes":[{"identity":identity,"actors":n,"pak":archive}
                  for identity,n,_,archive in rows],
        "manifest":str(MANIFEST)
    },sort_keys=True),flush=True)
if __name__=="__main__":run()
