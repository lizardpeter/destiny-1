#!/usr/bin/env python3
"""Verify retail source meshes for actual BP_TRV_ALight_Torch_02 child components.

This is an exact dependency closure: the original Blueprint's SCS_Node
ComponentTemplate references and StaticMesh fields determine the two child
UStaticMesh identities, not a material/filename similarity search.
"""
import json,struct,collections
from pathlib import Path
from fortnite_541_all_poi_coverage import SPLITS
from fortnite_541_factory_native_mesh_batch import locate,read_source
from fortnite_541_material_expression_probe import Catalog
import fortnite_541_r2_material_probe as retail
import fortnite_541_skylight_cube_probe as split

ROOT=Path("/tmp/fortnite541_torch_child_meshes")
MANIFEST=Path("/tmp/fortnite541_torch_child_meshes.tsv")
def fields(cat,ex):
    return cat.props(cat.export_data(ex))[0]
def ref(cat,ex,name):
    matches=[raw for n,k,meta,raw in fields(cat,ex) if n==name and k=="ObjectProperty"]
    if len(matches)>1:raise ValueError(f"multiple source {name} refs")
    return struct.unpack("<i",matches[0])[0] if matches else 0
def run():
    source=Path("/tmp/fortnite541_split_only_cdos.tsv").read_text().splitlines()
    identified=[line.split("\t") for line in source if "BP_TRV_ALight_Torch_02" in line]
    if len(identified)!=1 or identified[0][1]!="18":raise ValueError("original torch CDO count changed")
    identity,placed,stem=identified[0]
    p=Path(stem)
    c=Catalog(p.with_suffix(".uasset").read_bytes(),p.with_suffix(".uexp").read_bytes())
    templates=[]
    for i,ex in enumerate(c.exports,1):
        if c.class_name(ex)!="SCS_Node":continue
        cls_ref=ref(c,ex,"ComponentClass")
        tmpl_ref=ref(c,ex,"ComponentTemplate")
        if cls_ref==0 or tmpl_ref<=0 or c.path(cls_ref)!="/Script/Engine::StaticMeshComponent":continue
        template=c.exports[tmpl_ref-1]
        if c.class_name(template)!="StaticMeshComponent":raise ValueError("SCS source child template wrong class")
        mesh=ref(c,template,"StaticMesh")
        if not mesh:continue
        props=fields(c,template)
        vecs={}
        for name,kind,meta,raw in props:
            if name in ("RelativeLocation","RelativeRotation","RelativeScale3D"):
                if kind!="StructProperty" or len(raw)!=12:raise ValueError("authored transform malformed")
                vecs[name]=list(struct.unpack("<fff",raw))
        overrides=[]
        for name,kind,meta,raw in props:
            if name!="OverrideMaterials":continue
            if kind!="ArrayProperty" or meta!=["ObjectProperty"] or len(raw)<4:
                raise ValueError("original torch override materials changed source type")
            count=struct.unpack_from("<I",raw)[0]
            if count>32 or len(raw)!=4+4*count:
                raise ValueError("original torch override material UObject array malformed")
            overrides=[c.path(struct.unpack_from("<i",raw,4+4*j)[0])
                       for j in range(count)]
        templates.append({"SCS":c.path(i),"component":c.path(tmpl_ref),
            "mesh":c.path(mesh),"source_transform":vecs,
            "override_materials":overrides,
            "tagged_properties":[z[0] for z in props]})
    if len(templates)!=2:
        raise ValueError(f"expected two source SCS child StaticMesh templates, got {templates}")
    ix={"main":retail.load_index()}
    for chunk,sha in SPLITS:
        name="pakchunk1-WindowsClient.pak" if chunk=="chunk1" else f"pakchunk0_{chunk}-WindowsClient.pak"
        split.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/"+name
        split.INDEX_SHA=sha
        ix[chunk]=split.source()
    ROOT.mkdir(parents=True,exist_ok=True)
    manifest=[]
    for i,t in enumerate(templates):
        identity=t["mesh"]
        loc=locate(identity.split("::")[0],ix)
        if not loc:raise ValueError("authentic source child UStaticMesh package absent: "+identity)
        archive,base=loc
        dest=ROOT/str(i)
        for ext in (".uasset",".uexp"):
            dest.with_suffix(ext).write_bytes(read_source(archive,base+ext,ix))
        manifest.append((identity,placed,str(dest)))
        t["archive"]=archive
        t["original_source_files"]=[base+".uasset",base+".uexp"]
        pkg=Catalog(dest.with_suffix(".uasset").read_bytes(),dest.with_suffix(".uexp").read_bytes())
        t["source_material_imports"]=[pkg.path(-j) for j in range(1,len(pkg.imports)+1)
                                       if "Material" in pkg.path(-j)][:20]
    MANIFEST.write_text("".join(f"{item}\t{count}\t{path}\n" for item,count,path in manifest))
    print("FORTNITE_541_ORIGINAL_TORCH_CHILD_MESHES "+json.dumps({
        "original_class":identified[0][0],"actor_count":int(placed),
        "source_child_components":templates,
        "authenticated_source_packages":len(manifest),
        "exact_mesh_manifest":str(MANIFEST),
    },sort_keys=True),flush=True)
if __name__=="__main__":run()
