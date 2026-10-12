#!/usr/bin/env python3
"""Validate native UE4.21 original s3 paint source Texture2D BC top mips.

These are precisely the three extra source-painted albedos admitted by the
universal six-color neutral material path. Verify every original SHA1
PAK entry/payload, UE cooked Texture2D dimensions and block-byte bounds.
"""
import json,struct
from fortnite_541_all_poi_coverage import SPLITS
from fortnite_541_material_expression_probe import Catalog
import fortnite_541_skylight_cube_probe as source

SAMPLES=[
 ("Gravel","Packages/DS_Fortnight/WhiteRockCustom_D"),
 ("Road","Packages/DS_Fortnight/SM/Textures/T_Street_Road_D"),
 ("Arid","Environments/Sets/Arid/Textures/T_desert_sand_base_C"),
]
def u32(b,i):return struct.unpack_from("<I",b,i)[0]
def one(index,paint,original):
    payloads={ext:source.payload(index[original+ext])
              for ext in (".uasset",".uexp",".ubulk")}
    c=Catalog(payloads[".uasset"],payloads[".uexp"])
    matches=[e for e in c.exports if c.class_name(e)=="Texture2D"]
    if len(matches)!=1:raise ValueError("source "+paint+" original Texture2D class cardinality unexpected")
    raw=c.export_data(matches[0])
    props,offset=c.props(raw)
    cooked=raw[offset:]
    width,height,depth=struct.unpack_from("<III",cooked,28)
    name_length=u32(cooked,40)
    if name_length not in (7,8,12):raise ValueError("original source BC format FString length unexpected")
    kind=cooked[44:44+name_length].rstrip(bytes([0])).decode("ascii")
    first_mip,mip_count,slices=struct.unpack_from("<III",cooked,44+name_length)
    offset=44+name_length+12
    flags,stored,count=struct.unpack_from("<III",cooked,offset)
    signed=struct.unpack_from("<q",cooked,offset+12)[0]
    mw,mh,md=struct.unpack_from("<III",cooked,offset+20)
    original_bulk_offset=len(payloads[".uasset"])+len(payloads[".uexp"])-4+signed
    per_block={"PF_DXT1":8,"PF_DXT3":16,"PF_DXT5":16,"PF_BC4":8,"PF_BC5":16}
    if kind not in per_block:raise ValueError(f"source {paint} format {kind} not supported by native BC decoder")
    expect=((mw+3)//4)*((mh+3)//4)*per_block[kind]
    valid=(flags==0x501 and first_mip<=13 and mip_count in range(1,17)
           and slices==1
           and (width>>first_mip)==mw and (height>>first_mip)==mh and depth==md==1
           and count==stored==expect and
           0<=original_bulk_offset and
           original_bulk_offset+expect<=len(payloads[".ubulk"]))
    if not valid:raise ValueError(f"source {paint} BC image byte bounds invalid: "+json.dumps({
        "header_dimensions": [width,height,depth],"mip_dimensions":[mw,mh,md],
        "pixel_format":kind,"flags":hex(flags),
        "first_resident_mip":first_mip,"mip_count":mip_count,"slices":slices,"stored_bytes":stored,
        "bulk_count":count,"expected_bc_bytes":expect,
        "original_bulk_offset":original_bulk_offset,
        "ubulk_bytes":len(payloads[".ubulk"]),
        "signed_source_bulk_offset":signed
    },sort_keys=True))
    return {"paint":paint,"source_texture":original,"width":width,
        "height":height,"resident_width":mw,"resident_height":mh,
        "first_resident_mip":first_mip,"pixel_format":kind,"first_mip_bytes":expect,
        "original_BC_top_mip_verified":valid,"source_bulk_bytes":len(payloads[".ubulk"])}
def main():
    sha=dict(SPLITS)["s3"]
    source.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_s3-WindowsClient.pak"
    source.INDEX_SHA=sha
    idx=source.source()
    evidence=[]
    for name,path in SAMPLES:
        item=one(idx,name,path)
        print("ATHENA_541_ORIGINAL_S3_LANDSCAPE_TEXTURE_MIP "+json.dumps(item,sort_keys=True),flush=True)
        evidence.append(item)
    print("ATHENA_541_FIVE_PAINT_SOURCE_TEXTURES_VERIFIED "+json.dumps({
        "extra_albedos":len(evidence),"source_top_mip_bytes":sum(x["first_mip_bytes"] for x in evidence),
        "original_s3_index_sha1":sha
    },sort_keys=True),flush=True)
if __name__=="__main__":main()
