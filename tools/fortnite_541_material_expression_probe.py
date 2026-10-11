#!/usr/bin/env python3
"""Read real SHA-1-verified UE4.21 Fortnite 5.41 cooked source material nodes.
No guessed shader interpretation; print exact UObject/FProperty reference paths.
No copyrighted source assets are persisted or uploaded.
"""
from collections import Counter
import json
from pathlib import Path
import struct
import fortnite_541_r2_material_probe as r2

def u32(data,p):return struct.unpack_from("<I",data,p)[0]
def i32(data,p):return struct.unpack_from("<i",data,p)[0]
def i64(data,p):return struct.unpack_from("<q",data,p)[0]

class Catalog:
    def __init__(self, header, companion):
        if len(header)<64 or u32(header,0)!=0x9e2a83c1 or i32(header,4)!=-7:
            raise ValueError("not source UE4.21 cooked package header")
        self.header,self.companion=header,companion
        _,at=r2.fstring(header,28)
        fields=struct.unpack_from("<10I",header,at)
        name_count,name_offset=fields[1:3]
        export_count,export_offset=fields[5:7]
        import_count,import_offset=fields[7:9]
        depends_offset=fields[9]
        if (name_count>200000 or import_count>1000000 or export_count>1000000
            or import_offset+import_count*28!=export_offset
            or export_offset+export_count*104!=depends_offset):
            raise ValueError("source name/import/export table stride not retail verified")
        self.names=[]
        at=name_offset
        for _ in range(name_count):
            name,at=r2.fstring(header,at)
            self.names.append(name)
            at+=4
        self.imports=[]
        for k in range(import_count):
            p=import_offset+k*28
            self.imports.append({
                "class_name":self.name(u32(header,p+8)),
                "outer":i32(header,p+16),
                "name_index":u32(header,p+20),
                "name_number":u32(header,p+24),
            })
        self.exports=[]
        for k in range(export_count):
            p=export_offset+k*104
            self.exports.append({
                "class":i32(header,p),
                "outer":i32(header,p+12),
                "name_index":u32(header,p+16),
                "name_number":u32(header,p+20),
                "size":i64(header,p+28),
                "offset":i64(header,p+36),
            })
    def name(self,idx):
        if idx>=len(self.names):raise ValueError("source FName index out of bounds")
        return self.names[idx]
    def fname(self,raw):
        index,number=struct.unpack_from("<II",raw,0)
        return self.name(index)+(f"#{number}" if number else "")
    def value(self,ref):
        if ref==0:return "null"
        if ref<0:
            record=self.imports[-ref-1]
        else:
            record=self.exports[ref-1]
        return self.name(record["name_index"])+(f'#{record["name_number"]}' if record["name_number"] else '')
    def path(self,ref):
        seen=set()
        parts=[]
        while ref:
            if ref in seen or len(parts)>1000:raise ValueError("source UObject outer chain cycle")
            seen.add(ref)
            record=self.imports[-ref-1] if ref<0 else self.exports[ref-1]
            parts.append(self.value(ref))
            ref=record["outer"]
        return "::".join(reversed(parts))
    def class_name(self,ex):
        return self.value(ex["class"])
    def export_data(self,ex):
        at=ex["offset"]-len(self.header)
        end=at+ex["size"]
        if at<0 or end>len(self.companion):
            raise ValueError("source export outside authenticated UEXP")
        return self.companion[at:end]
    def props(self,data):
        props=[]
        pos=0
        for _ in range(20000):
            fname=self.fname(data[pos:pos+8])
            pos+=8
            if fname=="None":return props,pos
            kind=self.fname(data[pos:pos+8])
            pos+=8
            size=i32(data,pos)
            array_index=i32(data,pos+4)
            pos+=8
            if size<0 or array_index<0:
                raise ValueError("invalid source property size or index")
            extra=[]
            if kind=="StructProperty":
                extra.append(self.fname(data[pos:pos+8]))
                pos+=24
            elif kind=="BoolProperty":
                extra.append(data[pos])
                pos+=1
            elif kind in ["ByteProperty","EnumProperty","ArrayProperty","SetProperty"]:
                extra.append(self.fname(data[pos:pos+8]))
                pos+=8
            elif kind=="MapProperty":
                extra=[self.fname(data[pos:pos+8]),self.fname(data[pos+8:pos+16])]
                pos+=16
            guid=data[pos]
            pos+=1
            if guid not in [0,1]: raise ValueError("unexpected source property GUID flag")
            if guid:pos+=16
            raw=data[pos:pos+size]
            if len(raw)!=size:raise ValueError("source tagged property truncated")
            props.append((fname,kind,extra,raw))
            pos+=size
        raise ValueError("source tagged property bound exceeded")

def audit_one(base, entries):
    paths={}
    for ext in [".uasset",".uexp"]:
        matches=[(path,record) for path,record in entries.items() if path.endswith(base+ext)]
        if len(matches)!=1:raise ValueError(f"original material {base+ext}: matches={len(matches)}")
        paths[ext]=r2.source_payload(matches[0][1])
    catalog=Catalog(paths[".uasset"],paths[".uexp"])
    census=Counter()
    samples=[]
    links=[]
    errors=[]
    for i,ex in enumerate(catalog.exports,1):
        class_name=catalog.class_name(ex)
        if not class_name.startswith("MaterialExpression"):continue
        census[class_name]+=1
        try:
            props,_=catalog.props(catalog.export_data(ex))
            references=[]
            input_links=[]
            parameters=[]
            for property_name,kind,extra,raw in props:
                if kind in ["ObjectProperty","ClassProperty"] and len(raw)==4:
                    ref=i32(raw,0)
                    references.append({"name":property_name,"target":ref,"path":catalog.path(ref)})
                if kind=="NameProperty" and len(raw)==8:
                    parameters.append({"name":property_name,"value":catalog.fname(raw)})
                if kind=="StructProperty" and extra==["ExpressionInput"] and len(raw)==40:
                    ref=i32(raw,0)
                    input_links.append({"name":property_name,"target":ref,"path":catalog.path(ref),"source_40_bytes":raw.hex()})
            record={"export":i,"type":class_name,"object":catalog.value(i),
                    "references":references,"inputs":input_links,"parameters":parameters}
            if "TextureSample" in class_name:
                samples.append(record)
            elif any(k in class_name for k in ["MaterialFunctionCall","LandscapeLayerBlend",
                                              "LandscapeLayerSample","LandscapeLayerSwitch",
                                              "LandscapeLayerCoords","TextureCoordinate"]):
                links.append(record)
        except Exception as error:
            errors.append({"export":i,"class":class_name,"error":str(error)})
    return {"source_package_suffix":base,"expression_count":sum(census.values()),
            "class_counts":dict(sorted(census.items())),
            "texture_samples":samples,"graph_links":links,"unresolved":errors}
def audit_landscape_paint_layers(section,entries):
    suffix=f"/Maps/Landscape/Athena_Terrain_LS_{section:02}"
    payload=[]
    for extension in [".umap",".uexp"]:
        matches=[record for path,record in entries.items() if path.endswith(suffix+extension)]
        if len(matches)!=1:raise ValueError("original landscape source package missing: "+suffix+extension)
        payload.append(r2.source_payload(matches[0]))
    catalog=Catalog(*payload)
    combinations=Counter()
    components=0
    for export in catalog.exports:
        if catalog.class_name(export)!="LandscapeComponent":continue
        components+=1
        fields,_=catalog.props(catalog.export_data(export))
        for name,kind,meta,raw in fields:
            if name!="WeightmapLayerAllocations":continue
            if kind!="ArrayProperty" or meta!=["StructProperty"] or len(raw)<53:
                raise ValueError("original landscape paint is not typed source struct array")
            count=u32(raw,0)
            if count>64 or len(raw)!=53+105*count:
                raise ValueError("original landscape source paint array stride does not match")
            for index in range(count):
                record=raw[53+105*index:53+105*(index+1)]
                layer_fields,consumed=catalog.props(record)
                if consumed!=105:raise ValueError("original paint record trailing bytes")
                layer_info=[r for n,k,e,r in layer_fields if n=="LayerInfo" and k=="ObjectProperty"]
                if len(layer_info)!=1:raise ValueError("original source LayerInfo reference missing")
                ref=i32(layer_info[0],0)
                combinations[catalog.path(ref)]+=1
    return {"section":section,"components":components,"layer_info_allocation_counts":dict(combinations)}

def audit_texture_mip(suffix,entries):
    original={}
    for ext in [".uasset",".uexp",".ubulk"]:
        matches=[record for path,record in entries.items() if path.endswith(suffix+ext)]
        if len(matches)!=1:raise ValueError("original texture source missing: "+suffix+ext)
        original[ext]=r2.source_payload(matches[0])
    catalog=Catalog(original[".uasset"],original[".uexp"])
    tex=[record for record in catalog.exports if catalog.class_name(record)=="Texture2D"]
    if len(tex)!=1:raise ValueError("expected exactly one source Texture2D export")
    props,offset=catalog.props(catalog.export_data(tex[0]))
    cooked=catalog.export_data(tex[0])[offset:]
    width,height,depth=struct.unpack_from("<III",cooked,28)
    format_size=u32(cooked,40)
    if format_size not in [7,8,12]:raise ValueError("unrecognized authentic pixel format")
    fmt=cooked[44:44+format_size].rstrip(bytes([0])).decode()
    if fmt not in ["PF_DXT1","PF_DXT3","PF_DXT5","PF_BC4","PF_BC5","PF_B8G8R8A8"]:
        raise ValueError("unsupported original texture pixel format "+fmt)
    flags_at=44+format_size+12
    flags,stored,count=struct.unpack_from("<III",cooked,flags_at)
    signed_offset=i64(cooked,flags_at+12)
    mip_w,mip_h,mip_d=struct.unpack_from("<III",cooked,flags_at+20)
    bulk_offset=len(original[".uasset"])+len(original[".uexp"])-4+signed_offset
    bytes_per_block={"PF_DXT1":8,"PF_DXT3":16,"PF_DXT5":16,"PF_BC4":8,"PF_BC5":16}
    expected=(mip_w*mip_h*4 if fmt=="PF_B8G8R8A8"
              else ((mip_w+3)//4)*((mip_h+3)//4)*bytes_per_block[fmt])
    valid=(flags==0x501 and width==mip_w and height==mip_h and depth==mip_d==1
           and stored==count==expected and bulk_offset>=0 and bulk_offset+expected<=len(original[".ubulk"]))
    return {"suffix":suffix,"width":width,"height":height,"format":fmt,
            "bulk_flags":hex(flags),"first_mip_bytes":stored,
            "actual_bulk_offset":bulk_offset,"source_mip_bounds_verified":valid}

def main():
    entries=r2.load_index()
    bases=[
        "/Environments/Landscape/Material/M_Athena_Terrain_Master",
        "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Grass_01",
        "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Rock_01",
        "/Environments/Landscape/MaterialFunctions/Standard/MF_Athena_Forest_01",
        "/Environments/Landscape/MaterialFunctions/MF_FarmGrass_Colors",
        "/Environments/Landscape/MaterialFunctions/MF_LawnGrassColoration",
    ]
    audited=[]
    for base in bases:
        result=audit_one(base,entries)
        audited.append(result)
        print("FORTNITE_REAL_MATERIAL_GRAPH "+json.dumps({
            "path":base,"nodes":result["expression_count"],
            "classes":result["class_counts"],
            "texture_samples":result["texture_samples"][:32],
            "graph_links":result["graph_links"][:32],
            "unresolved":result["unresolved"][:8],
        },sort_keys=True),flush=True)
    for suffix in [
        "/Environments/Landscape/Textures/T_Athena_Terrain_CombinedColors_01",
        "/Environments/Landscape/Textures/T_Athena_ForestFloor_D",
        "/Environments/Landscape/Textures/T_Athena_Grass_Farm_ColorMatched_D_2",
    ]:
        proof=audit_texture_mip(suffix,entries)
        print("FORTNITE_REAL_TEXTURE_MIP "+json.dumps(proof,sort_keys=True),flush=True)
        if not proof["source_mip_bounds_verified"]:
            raise ValueError("actual original texture top mip failed exact source layout validation")
    paint=[]
    for section in range(6):
        result=audit_landscape_paint_layers(section,entries)
        paint.append(result)
        print("FORTNITE_REAL_LANDSCAPE_PAINT "+json.dumps(result,sort_keys=True),flush=True)
    Path("fortnite-541-material-expression-audit.json").write_text(
        json.dumps({"material_graphs":audited,"paint_sections":paint},indent=2),encoding="utf8")
    print("FORTNITE_REAL_MATERIAL_AUDIT_COMPLETE "+json.dumps({
        "packages":len(audited),"sampled_texture_nodes":sum(len(a["texture_samples"]) for a in audited),
        "unresolved":sum(len(a["unresolved"]) for a in audited),
        "terrain_components":sum(section["components"] for section in paint)
    }),flush=True)
if __name__=="__main__":
    main()
