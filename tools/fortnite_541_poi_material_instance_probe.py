#!/usr/bin/env python3
"""Authenticate source material instances used by actual Factory mesh slots.

Never search by a similarly named stock texture: follow exact MaterialInterface
UObject in StaticMaterials, find original MIC UTexture2D parameters, and
record their source identities for the universal renderer.
"""
import json,struct
from fortnite_541_factory_native_mesh_batch import locate,read_source
from fortnite_541_all_poi_coverage import SPLITS,ROOT
import fortnite_541_r2_material_probe as main
import fortnite_541_skylight_cube_probe as split
from fortnite_541_material_expression_probe import Catalog
PACKAGES=[
    "Environments/Props/Industrial/Materials/MI_ShippingContainer_01",
    "Packages/DS_Fortnite_Terrain_NoLOD/Materials/M_Terrain_Cave",
    "Packages/DS_Fortnite_Terrain_NoLOD/Materials/M_Terrain_Cliff_White",
]
def run():
    indexes={"main":main.load_index()}
    for archive,sha in SPLITS:
        path="pakchunk1-WindowsClient.pak" if archive=="chunk1" else f"pakchunk0_{archive}-WindowsClient.pak"
        split.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/"+path
        split.INDEX_SHA=sha
        indexes[archive]=split.source()
    for source in PACKAGES:
        full=ROOT+source
        found=locate("/Game/"+source+"::"+source.rsplit("/",1)[-1],indexes)
        if found is None:
            print("FORTNITE_SOURCE_MATERIAL_PROBE "+json.dumps({"material":source,"present":False}),flush=True)
            continue
        archive,base=found
        cat=Catalog(read_source(archive,base+".uasset",indexes),
                    read_source(archive,base+".uexp",indexes))
        result=[]
        for i,ex in enumerate(cat.exports,1):
            typ=cat.class_name(ex)
            if typ not in ("MaterialInstanceConstant","Material","MaterialInstance"):
                continue
            props,_=cat.props(cat.export_data(ex))
            rows=[]
            for n,k,meta,v in props:
                item={"name":n,"kind":k,"meta":meta,"length":len(v)}
                if k=="ObjectProperty" and len(v)==4:
                    ref=struct.unpack("<i",v)[0]
                    item["source_object"]=cat.path(ref) if ref else None
                if k=="ArrayProperty" and len(v)>=4:
                    item["count"]=struct.unpack_from("<I",v)[0]
                    item["prefix"]=v[:125].hex()
                    if n=="TextureParameterValues":
                        none=struct.pack("<II",cat.names.index("None"),0)
                        wrapper,_=cat.props(v[4:]+none)
                        if len(wrapper)!=1 or wrapper[0][1]!="StructProperty":
                            raise ValueError("retail material texture parameter aggregate changed")
                        inner=wrapper[0][3]
                        cursor=0
                        decoded=[]
                        for j in range(item["count"]):
                            tagged,used=cat.props(inner[cursor:])
                            if used<=0:raise ValueError("original texture parameter struct failed to advance")
                            cursor+=used
                            param={}
                            for pn,pk,pmeta,praw in tagged:
                                if pn=="ParameterInfo" and pk=="StructProperty":
                                    info,_=cat.props(praw)
                                    param["info"]=[{"name":nn,"kind":nk,
                                        "value":cat.fname(nraw) if nk=="NameProperty" and len(nraw)==8 else None}
                                        for nn,nk,nmeta,nraw in info]
                                elif pn=="ParameterValue" and pk=="ObjectProperty" and len(praw)==4:
                                    ref=struct.unpack("<i",praw)[0]
                                    param["texture"]=cat.path(ref) if ref else None
                                else:param[pn]={"kind":pk,"size":len(praw)}
                            decoded.append(param)
                        item["original_texture_parameters"]=decoded
                        item["source_bytes_used"]=cursor
                        item["source_bytes_total"]=len(inner)
                rows.append(item)
            result.append({"name":cat.value(i),"class":typ,"fields":rows})
        print("FORTNITE_SOURCE_MATERIAL_PROBE "+json.dumps({
            "material":source,"archive":archive,"source_classes":[cat.class_name(e) for e in cat.exports],
            "exported_materials":result
        },sort_keys=True),flush=True)
if __name__=="__main__":run()
