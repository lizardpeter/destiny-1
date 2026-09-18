#!/usr/bin/env python3
"""Decode D1 ROI PS4 sampler tags into native Gnm S# descriptor fields.

Validated D1 class 0x80801A42 is 24 bytes: u64 size + four native sampler
words. Raw words are canonical; source-correlated Gnm labels are convenience
labels only. A same-sized tag of another class is never decoded as a sampler.
"""
from __future__ import annotations
import argparse,json,struct,sys
from pathlib import Path
HERE=Path(__file__).resolve().parent;sys.path.insert(0,str(HERE))
from d1_entry_extract import EntryReader
SAMPLER_CLASS='80801A42'
WRAP={0:'Wrap',1:'Mirror',2:'ClampLastTexel',3:'MirrorOnceLastTexel',4:'ClampHalfBorder',5:'MirrorOnceHalfBorder',6:'ClampBorder',7:'MirrorOnceBorder'}
FILTER={0:'Point',1:'Bilinear',2:'AnisoPoint',3:'AnisoBilinear'};ZFILTER={0:'None',1:'Point',2:'Linear'};MIPFILTER={0:'None',1:'Point',2:'Linear'};BORDER={0:'TransBlack',1:'OpaqueBlack',2:'OpaqueWhite',3:'FromTable'}
def field(w,mask,shift):return (w&mask)>>shift
def signed(v,bits):
 sign=1<<(bits-1);return v-(1<<bits) if v&sign else v
def decode_blob(b:bytes)->dict:
 if len(b)!=24:raise ValueError(f'expected 24-byte D1 PS4 sampler tag, got {len(b)}')
 declared=struct.unpack_from('<Q',b,0)[0]
 if declared!=len(b):raise ValueError(f'declared size {declared} != actual {len(b)}')
 w0,w1,w2,w3=struct.unpack_from('<4I',b,8);cx=field(w0,7,0);cy=field(w0,0x38,3);cz=field(w0,0x1c0,6);mag=field(w2,0x00300000,20);minf=field(w2,0x00c00000,22);zf=field(w2,0x03000000,24);mip=field(w2,0x0c000000,26);lb=field(w2,0x3fff,0);border=field(w3,0xc0000000,30)
 return {'declared_file_size':declared,'descriptor_offset':8,'descriptor_hex':b[8:].hex(),'words_hex':[f'{x:08X}' for x in (w0,w1,w2,w3)],'wrap_x':{'value':cx,'gnm_name':WRAP.get(cx)},'wrap_y':{'value':cy,'gnm_name':WRAP.get(cy)},'wrap_z':{'value':cz,'gnm_name':WRAP.get(cz)},'max_aniso_ratio_raw':field(w0,0xe00,9),'depth_compare_raw':field(w0,0x7000,12),'force_unnormalized_raw':field(w0,0x8000,15),'aniso_threshold_raw':field(w0,0x70000,16),'force_degamma_raw':field(w0,0x100000,20),'filter_reduction_mode_raw':field(w0,0x60000000,29),'min_lod_raw':field(w1,0xfff,0),'max_lod_raw':field(w1,0xfff000,12),'lod_bias_raw_unsigned14':lb,'lod_bias_raw_signed14':signed(lb,14),'lod_bias_secondary_raw':field(w2,0xfc000,14),'mag_filter':{'value':mag,'gnm_name':FILTER.get(mag)},'min_filter':{'value':minf,'gnm_name':FILTER.get(minf)},'z_filter':{'value':zf,'gnm_name':ZFILTER.get(zf)},'mip_filter':{'value':mip,'gnm_name':MIPFILTER.get(mip)},'border_color':{'value':border,'gnm_name':BORDER.get(border)},'border_color_ptr_raw':field(w3,0xfff,0)}
def decode_validated_class(class_hash:str,b:bytes)->dict:
 """Class-aware entry point: layout coincidence is not evidence of ownership."""
 if str(class_hash).upper().removeprefix('0X')!=SAMPLER_CLASS:raise ValueError(f'class {class_hash} is not validated D1 PS4 sampler class {SAMPLER_CLASS}')
 return decode_blob(b)
def main():
 ap=argparse.ArgumentParser();ap.add_argument('pkg',type=Path);ap.add_argument('--runtime',type=Path,required=True);ap.add_argument('--tag-hash',action='append',required=True);ap.add_argument('-o','--output',type=Path);a=ap.parse_args();r=EntryReader(a.pkg,a.runtime);by={e['tag_hash'].upper():e for e in r.entries};rows=[]
 for raw in a.tag_hash:
  h=raw.upper().removeprefix('0X');e=by.get(h)
  if e is None:rows.append({'tag_hash':h,'present':False});continue
  ok=e['reference'].upper()==SAMPLER_CLASS;row={'tag_hash':h,'present':True,'entry_index':e['index'],'class_hash':e['reference'],'type':e['type'],'subtype':e['subtype'],'available':r.available(e['index']),'class_matches_validated_sampler':ok}
  if row['available']:
   b=r.entry(e['index']);row['raw_hex']=b.hex()
   if ok:row['decoded']=decode_validated_class(e['reference'],b)
   else:row['decode_withheld']='class hash does not match validated sampler class 80801A42'
  rows.append(row)
 rep={'package':str(r.pkg),'platform':r.h['platform'],'validated_sampler_class':SAMPLER_CLASS,'samplers':rows};text=json.dumps(rep,indent=2)
 if a.output:a.output.parent.mkdir(parents=True,exist_ok=True);a.output.write_text(text+'\n');print('wrote',a.output)
 else:print(text)
if __name__=='__main__':main()
