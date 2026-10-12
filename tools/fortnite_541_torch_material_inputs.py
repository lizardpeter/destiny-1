#!/usr/bin/env python3
"""Source material graph census for Fortnite 5.41 torch flame and bloom.

Only the explicit original SCS child StaticMesh material references:
Flame.OverrideMaterials[0] -> MI_Fire_Campfire_Mesh_Torch
Bloom mesh.StaticMaterials -> M_FakeVolumeGlow
"""
import json,collections,struct
from fortnite_541_all_poi_coverage import SPLITS
from fortnite_541_factory_native_mesh_batch import locate,read_source
from fortnite_541_material_expression_probe import Catalog
import fortnite_541_r2_material_probe as retail
import fortnite_541_skylight_cube_probe as split
IDENTITIES=(
    "/Game/Athena/Items/Traps/Campfire/Effects/MI_Fire_Campfire_Mesh_Torch::MI_Fire_Campfire_Mesh_Torch",
    "/Game/Packages/Fortress_Transylvania/Test_Assets/Materials/M_FakeVolumeGlow::M_FakeVolumeGlow",
)
def run():
    indexes={"main":retail.load_index()}
    for archive,sha in SPLITS:
        pak="pakchunk1-WindowsClient.pak" if archive=="chunk1" else f"pakchunk0_{archive}-WindowsClient.pak"
        split.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/"+pak
        split.INDEX_SHA=sha
        indexes[archive]=split.source()
    for original in IDENTITIES:
        loc=locate(original.split("::")[0],indexes)
        if not loc:raise ValueError("original flame/bloom source UMaterial absent: "+original)
        archive,base=loc
        c=Catalog(read_source(archive,base+".uasset",indexes),
                  read_source(archive,base+".uexp",indexes))
        census=collections.Counter(c.class_name(e) for e in c.exports)
        outputs=[]
        for i,e in enumerate(c.exports,1):
            cls=c.class_name(e)
            if not (cls.startswith("MaterialExpression") or
                    cls in ("Material","MaterialInstanceConstant")):continue
            props,_=c.props(c.export_data(e))
            tags=[]
            for name,kind,meta,v in props:
                x={"name":name,"kind":kind,"size":len(v),"meta":meta}
                if kind=="ObjectProperty" and len(v)==4:
                    id=struct.unpack("<i",v)[0]
                    x["path"]=c.path(id) if id else None
                elif kind=="NameProperty" and len(v)==8:
                    x["value"]=c.fname(v)
                elif kind=="ArrayProperty" and len(v)>=4:
                    x["count"]=struct.unpack_from("<I",v)[0]
                tags.append(x)
            outputs.append({"object":c.path(i),"class":cls,"tags":tags[:85]})
        print("FORTNITE_TORCH_SOURCE_MATERIAL_SHADER_FRONTIER "+json.dumps({
            "original":original,"archive":archive,
            "class_census":census.most_common(45),
            "source_exports":outputs[:120]
        },sort_keys=True),flush=True)
if __name__=="__main__":run()
