#!/usr/bin/env python3
"""Diagnose actual Fortnite 5.41 sky and missing full-resolution level source.
Uses SHA1-verified original PAK bytes; no invented landscape/sky metadata.
"""
import json,struct,collections,statistics
import fortnite_541_r2_material_probe as r2
import fortnite_541_skylight_cube_probe as s4
from fortnite_541_material_expression_probe import Catalog
def bc3_stats(blocks):
    # BC3 color block, 4x4 image, eight-byte BC3 alpha preceding BC1 RGB.
    # Original skylight source SRGB=false, so sampled bytes are linear.
    face_stats=[]
    for face in range(6):
        raw=blocks[face*65536:(face+1)*65536]
        total=[0,0,0]; lum_values=[]; nonblack=0
        for b in range(0,len(raw),16):
            a0,a1=struct.unpack_from("<BB",raw,b)
            alpha_bits=int.from_bytes(raw[b+2:b+8],"little")
            c0,c1,idx=struct.unpack_from("<HHI",raw,b+8)
            def rgb565(c):
                return (((c>>11)&31)*255//31,((c>>5)&63)*255//63,(c&31)*255//31)
            v0=rgb565(c0);v1=rgb565(c1)
            pal=[v0,v1]
            if c0>c1:
                pal+=[tuple((2*v0[j]+v1[j])//3 for j in range(3)),
                      tuple((v0[j]+2*v1[j])//3 for j in range(3))]
            else:
                pal+=[tuple((v0[j]+v1[j])//2 for j in range(3)),(0,0,0)]
            for n in range(16):
                r,g,bb=pal[(idx>>(2*n))&3]
                total[0]+=r;total[1]+=g;total[2]+=bb
                brightness=(r+g+bb)/3
                lum_values.append(brightness)
                nonblack+=brightness>8
        face_stats.append({"source_face":face,"mean_linear_rgb_8bit":[round(x/65536,2) for x in total],
            "mean_linear_luma_8bit":round(sum(total)/3/65536,2),
            "fraction_pixels_gt8":round(nonblack/65536,4),
            "p05":round(sorted(lum_values)[3276],2),
            "p50":round(sorted(lum_values)[32768],2),
            "p95":round(sorted(lum_values)[62259],2)})
    return face_stats
def root_streams():
    ix=r2.load_index()
    prefix="FortniteGame/Content/Athena/Maps/Athena_Terrain"
    cat=Catalog(r2.source_payload(ix[prefix+".umap"]),r2.source_payload(ix[prefix+".uexp"]))
    classes=collections.Counter(cat.class_name(e) for e in cat.exports)
    streamed=[]
    for i,e in enumerate(cat.exports,1):
        cls=cat.class_name(e)
        if not cls.startswith("LevelStreaming"):continue
        raw=cat.export_data(e)
        fields,n=cat.props(raw)
        attrs=[]
        for name,typ,extra,payload in fields:
            entry={"name":name,"kind":typ,"size":len(payload)}
            if typ=="NameProperty" and len(payload)==8:
                entry["value"]=cat.fname(payload)
            elif typ in ("ObjectProperty","ClassProperty") and len(payload)==4:
                ref=struct.unpack("<i",payload)[0]
                entry["value"]=cat.path(ref) if ref else None
            elif typ=="SoftObjectProperty" and len(payload)>=12:
                entry["path"]=cat.fname(payload[:8])
                entry["subpath_length"]=struct.unpack_from("<i",payload,8)[0]
                if 0<entry["subpath_length"]<1000:
                    entry["subpath_bytes"]=payload[12:80].hex()
            elif typ=="StructProperty" and len(payload)==12:
                entry["xyz"]=struct.unpack("<fff",payload)
            elif typ=="StrProperty":
                entry["raw_head"]=payload[:100].hex()
            attrs.append(entry)
        streamed.append({"export":cat.path(i),"class":cls,"properties":attrs})
    return {"all_exports":len(cat.exports),"streaming_entries":len(streamed),
        "class_census":classes.most_common(10),"levels":streamed[:30]}
def main():
    entries=s4.source()
    prefix="Packages/Fortress_Sky/TexturesHDR/T_AthenaSkylight"
    heads=[rec for k,rec in entries.items() if k.endswith(prefix+".uasset")]
    exps=[rec for k,rec in entries.items() if k.endswith(prefix+".uexp")]
    if len(heads)!=1 or len(exps)!=1:raise ValueError("source skylight export missing")
    cat=Catalog(s4.payload(heads[0]),s4.payload(exps[0]))
    record=next(ex for ex in cat.exports if cat.class_name(ex)=="TextureCube")
    asset=cat.export_data(record)
    props,n=cat.props(asset)
    cooked=asset[n:]
    if len(cooked)<393308 or cooked[44:52]!=b"PF_DXT5\x00":
        raise ValueError("source cubemap format not verified")
    blocks=cooked[92:393308]
    print("FORTNITE_AUTHENTIC_SKYLIGHT_PIXELS "+json.dumps({"source_texture":prefix,
        "original_SRGB":False,"faces":bc3_stats(blocks)}),flush=True)
    print("FORTNITE_AUTHENTIC_ROOT_STREAMED_LEVELS "+json.dumps(root_streams()),flush=True)
    sky_assets=[
        "Packages/Fortress_Sky/SkyDome/MaterialInstances/SkyDomeBasic01/Day_M_SkyDome_Inst_Basic01",
        "Packages/Fortress_Sky/SkyDome/MaterialInstances/SkyDomeBasic01/Morn_M_SkyDome_Inst_Basic01",
    ]
    for asset in sky_assets:
        headers=[v for k,v in entries.items() if k.endswith(asset+".uasset")]
        exports=[v for k,v in entries.items() if k.endswith(asset+".uexp")]
        if len(headers)!=1 or len(exports)!=1:continue
        c=Catalog(s4.payload(headers[0]),s4.payload(exports[0]))
        objs=[]
        for idx,ex in enumerate(c.exports,1):
            raw=c.export_data(ex)
            try:
                fields,at=c.props(raw)
                props=[]
                for name,kind,meta,payload in fields:
                    entry={"name":name,"kind":kind,"bytes":len(payload)}
                    if kind=="ObjectProperty" and len(payload)==4:
                        ref=struct.unpack("<i",payload)[0]
                        entry["source_ref"]=c.path(ref) if ref else None
                    elif kind=="ArrayProperty":
                        entry["count"]=struct.unpack_from("<I",payload)[0] if len(payload)>=4 else None
                        entry["head160"]=payload[:160].hex()
                    elif kind=="StructProperty" and len(payload) in (12,16):
                        entry["raw_floats"]=struct.unpack("<"+("f"*(len(payload)//4)),payload)
                    props.append(entry)
                objs.append({"name":c.value(idx),"class":c.class_name(ex),"props":props})
            except Exception as err:objs.append({"class":c.class_name(ex),"error":str(err)})
        print("FORTNITE_AUTHENTIC_DAY_SKY_MATERIAL "+json.dumps({"asset":asset,"exports":objs}),flush=True)
if __name__=="__main__":main()
