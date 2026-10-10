#!/usr/bin/env python3
"""Parse a locally decrypted UE4 v7 Pak index in memory, bounded and read-only."""
from pathlib import Path
import collections, struct,sys,hashlib
p=Path(sys.argv[1])
b=p.read_bytes()
sha=hashlib.sha1(b).hexdigest()
print("DECRYPTED_INDEX",p.name,"len",len(b),"sha1",sha,flush=True)
def u32(off):
 if off+4>len(b): raise ValueError("truncated")
 return struct.unpack_from("<I",b,off)[0]
def fstr(off):
 n=struct.unpack_from("<i",b,off)[0];off+=4
 if not n: return "",off
 if abs(n)>131072:raise ValueError("oversized fstring "+str(n))
 c=n if n>0 else -n*2
 if off+c>len(b):raise ValueError("truncated fstring")
 v=b[off:off+c];off+=c
 if n>0:
  if v[-1]!=0:raise ValueError("no terminator")
  return v[:-1].decode("utf8"),off
 if v[-2:]!=b"\0\0":raise ValueError("no terminator")
 return v[:-2].decode("utf16le"),off
off=0
mount,off=fstr(off)
total=u32(off);off+=4
print("MOUNT",repr(mount),"ENTRY_COUNT",total,flush=True)
if total>1000000:raise ValueError("implausible entry count")
maps=[]
methods=collections.Counter()
enc=0
for j in range(total):
 name,off=fstr(off)
 if off+48>len(b):raise ValueError("truncated entry "+str(j))
 offset,size,uncompressed,method=struct.unpack_from("<QQQI",b,off)
 off+=28+20
 if method:
  blocks=u32(off);off+=4
  if blocks>1000000:raise ValueError("bad blocks")
  off+=16*blocks
 if off+5>len(b):raise ValueError("truncated block extras")
 enc+=b[off]&1
 off+=5
 if off>len(b):raise ValueError("overrun")
 methods[method]+=1
 if name.lower().endswith(".umap"):maps.append(name)
 if j<3: print("FIRST_ENTRY",j,repr(name),"offset",offset,"stored",size,"raw",uncompressed,"method",method,flush=True)
print("DONE",total,"maps",len(maps),"enc_entries",enc,"methods",dict(methods),"end_offset",off,"index_size",len(b),flush=True)
print("MAPS_FIRST_45",repr(maps[:45]),flush=True)
print("ATHENA_MAPS_FIRST_100",repr([x for x in maps if "athena" in x.lower()][:100]),flush=True)
print("TERRAIN_MATCHES",repr([x for x in maps if "terrain" in x.lower()][:50]),flush=True)
