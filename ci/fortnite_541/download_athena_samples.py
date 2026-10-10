#!/usr/bin/env python3
"""Download a small, source-authored Fortnite 5.41 Athena map corpus.
Indexes and files are read from a public R2 endpoint; no game binaries executed.
No source objects are committed/published by this job."""
from pathlib import Path
import subprocess,struct,hashlib,json
buf=Path('/tmp/fortnite541-pak0-index.dec').read_bytes()
url='https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0-WindowsClient.pak'
out=Path('/tmp/fortnite541-atlas')
out.mkdir(exist_ok=True)
pak_size=4813653874
index_offset=4805651429
sparse=Path('/tmp/fortnite541-pak0-sparse.pak')
with sparse.open('wb') as f:
 f.seek(pak_size-1)
 f.write(b'\\0')
encrypted_index=Path('/tmp/fortnite541-pak0-index.enc').read_bytes()
with sparse.open('r+b') as f:
 f.seek(index_offset)
 f.write(encrypted_index)
footer=Path('/tmp/fortnite541-footer61')
subprocess.run(['curl','--fail','--silent','--show-error','--location','--retry','3',
                '--range',f'{pak_size-61}-{pak_size-1}',
                '--output',str(footer),
                'https://r2.houseofkublai.com/Fortnite/5.41/FortniteGame/Content/Paks/pakchunk0-WindowsClient.pak'],check=True)
assert footer.stat().st_size==61
with sparse.open('r+b') as f:
 f.seek(pak_size-61)
 f.write(footer.read_bytes())
wanted=[
'FortniteGame/Content/Athena/Maps/Athena_Terrain.umap',
'FortniteGame/Content/Athena/Maps/Athena_Terrain.uexp',
'FortniteGame/Content/Athena/Maps/Landscape/Athena_Terrain_LS_00.umap',
'FortniteGame/Content/Athena/Maps/Landscape/Athena_Terrain_LS_00.uexp',
'FortniteGame/Content/Athena/Maps/Streaming/Sublevel_X0Y0.umap',
'FortniteGame/Content/Athena/Maps/Streaming/Sublevel_X0Y0.uexp',
'FortniteGame/Content/Athena/Maps/Background/Athena_Background.umap',
'FortniteGame/Content/Athena/Maps/Background/Athena_Background.uexp',
]
def fstr(off):
 n=struct.unpack_from('<i',buf,off)[0];off+=4
 if not n:return '',off
 l=n if n>0 else -n*2
 z=buf[off:off+l];off+=l
 return z[:-1].decode('utf8') if n>0 else z[:-2].decode('utf-16-le'),off
mount,pos=fstr(0)
count=struct.unpack_from('<I',buf,pos)[0];pos+=4
records={}
for _ in range(count):
 path,pos=fstr(pos)
 offset,size,raw,method=struct.unpack_from('<QQQI',buf,pos);pos+=28
 sha=buf[pos:pos+20];pos+=20
 if method:
  bc=struct.unpack_from('<I',buf,pos)[0];pos+=4+16*bc
 enc=buf[pos]&1;pos+=5
 if path in wanted: records[path]=(offset,size,raw,method,sha,enc)
assert len(records)==len(wanted),(len(records),len(wanted))
for i,path in enumerate(wanted):
 offset,size,raw,method,sha,enc=records[path]
 if size>5_000_000 or method or enc:raise RuntimeError(f"unsupported map record {path} method {method} enc {enc} size {size}")
 # FPakEntry is 53 bytes for uncompressed UE4 v7 records.
 data_start=offset+53
 full_path=out/('map'+str(i)+Path(path).suffix)
 subprocess.run(['curl','--fail','--silent','--show-error','--location','--retry','3',
                 '--range',f'{data_start}-{data_start+size-1}','--output',str(full_path),url],check=True)
 data=full_path.read_bytes()
 header_file=out/('header'+str(i)+'.bin')
 subprocess.run(['curl','--fail','--silent','--show-error','--location','--retry','3',
                 '--range',f'{offset}-{offset+52}','--output',str(header_file),url],check=True)
 header=header_file.read_bytes()
 if len(header)!=53:raise RuntimeError('truncated source FPakEntry header')
 with sparse.open('r+b') as f:
  f.seek(offset)
  f.write(header)
  f.write(data)
 got=hashlib.sha1(data).digest()
 print('MAP_PAYLOAD',path,'offset',data_start,'size',len(data),
       'sha_expected',sha.hex(),'sha_actual',got.hex(),'verified',got==sha,
       'first48',data[:48].hex(),flush=True)
 if len(data)!=size:raise RuntimeError("unexpected range length")
 if not data.startswith(bytes.fromhex('c1832a9e')) and path.endswith('.umap'):
  print('PACKAGE_SIGNATURE_NOT_UE4',path,flush=True)
 # Keep only small temporary files: no uploads or artifacts.
print('DOWNLOAD_COMPLETE',len(wanted),'map package files',flush=True)

print('SPARSE_RETAIL_PAK_READY',str(sparse),'logical_bytes',sparse.stat().st_size,flush=True)
