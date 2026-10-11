#!/usr/bin/env python3
"""Read source-authored Fortnite BR TODM_CDO and sky/fog component fields.

Check for a source-backed sun direction before admitting a directional sun
into the one universal Athena renderer. Report metadata only, from SHA1
verified Fortnite 5.41 source PAK.
"""
import struct,json
import fortnite_541_skylight_cube_probe as r2
from fortnite_541_material_expression_probe import Catalog
ROOT="TimeOfDay/TODM/BR/TODM_BR"

def scalar(c,kind,blob):
    if kind=="FloatProperty" and len(blob)==4:
        return struct.unpack("<f",blob)[0]
    if kind=="IntProperty" and len(blob)==4:
        return struct.unpack("<i",blob)[0]
    if kind=="NameProperty" and len(blob)==8:
        return c.fname(blob)
    if kind=="StructProperty" and len(blob)==12:
        return list(struct.unpack("<fff",blob))
    if kind=="StructProperty" and len(blob)==16:
        return list(struct.unpack("<ffff",blob))
    if kind=="ObjectProperty" and len(blob)==4:
        ref=struct.unpack("<i",blob)[0]
        return c.path(ref) if ref else None
    return None
def child(c,buffer):
    props,_=c.props(buffer)
    rows=[]
    for name,kind,meta,raw in props:
        obj={"name":name,"type":kind,"meta":meta,"size":len(raw)}
        val=scalar(c,kind,raw)
        if val is not None:obj["value"]=val
        rows.append(obj)
    return rows

def run():
    r2.URL="https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0_s4-WindowsClient.pak"
    r2.INDEX_SHA="96a67f9eae257051576e368fdb61a6fb78b2f56a"
    ix=r2.source()
    head=next(rec for p,rec in ix.items() if p.endswith(ROOT+".uasset"))
    exp=next(rec for p,rec in ix.items() if p.endswith(ROOT+".uexp"))
    c=Catalog(r2.payload(head),r2.payload(exp))
    records=[]
    for i,ex in enumerate(c.exports,1):
        if ex["size"]>4_000_000:continue
        name=c.value(i)
        kind=c.class_name(ex)
        if not any(z in (name+" "+kind).lower()
                   for z in ("default__todm","light","fog","sky","sun","celestial","direction")):
            continue
        data=c.export_data(ex)
        try:
            props,_=c.props(data)
            fields=[]
            for n,k,meta,raw in props:
                obj={"name":n,"kind":k,"meta":meta,"size":len(raw)}
                v=scalar(c,k,raw)
                if v is not None:obj["value"]=v
                if n=="LightAndFogPhaseSettings" and k=="StructProperty":
                    fields2,n2=c.props(raw)
                    nested=[]
                    for sn,sk,smeta,sraw in fields2:
                        entry={"name":sn,"type":sk,"meta":smeta}
                        if sn in ("DirectionalLightValues","SkyLightValues","ExpHeightFogValues"):
                            try:entry["properties"]=child(c,sraw)
                            except Exception as e:entry["error"]=str(e)
                        nested.append(entry)
                    obj["phase_fields"]=nested
                fields.append(obj)
            records.append({"name":name,"class":kind,"path":c.path(i),"fields":fields})
        except Exception as err:records.append({"name":name,"class":kind,"error":str(err)})
    print("FORTNITE_ORIGINAL_SUN_LIGHT_FOG_DIRECTION_SOURCE "+
          json.dumps(records,sort_keys=True),flush=True)
if __name__=="__main__":run()
