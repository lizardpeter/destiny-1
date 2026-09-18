#!/usr/bin/env python3
"""Regression vectors for the exact 24-byte PS4 sampler descriptor decoder.
Vectors are recovered retail descriptors documented in spec/D1_MATERIALS_SHADERS.md.
"""
import importlib.util,struct
from pathlib import Path
P=Path(__file__).parents[1]/'tools'/'d1_ps4_sampler_probe.py';s=importlib.util.spec_from_file_location('sampler',P);m=importlib.util.module_from_spec(s);s.loader.exec_module(m)
def blob(words):return struct.pack('<Q4I',24,*words)
main_blob=blob((0x00000000,0x00F00000,0x0A503F80,0x00000000));main=m.decode_validated_class('80801A42',main_blob)
assert main['words_hex']==['00000000','00F00000','0A503F80','00000000'];assert [main[x]['value'] for x in ('wrap_x','wrap_y','wrap_z')]==[0,0,0];assert main['min_lod_raw']==0 and main['max_lod_raw']==3840;assert main['lod_bias_raw_signed14']==-128 and main['lod_bias_secondary_raw']==0;assert main['mag_filter']['value']==1 and main['min_filter']['value']==1 and main['mip_filter']['value']==2
cube=m.decode_validated_class('0x80801A42',blob((0x00000092,0x00F00000,0x0A503F80,0)));assert [cube[x]['value'] for x in ('wrap_x','wrap_y','wrap_z')]==[2,2,2]
circuit=m.decode_validated_class('80801a42',blob((0x000001B6,0x00F00000,0x0A503F80,0x80000000)));assert [circuit[x]['value'] for x in ('wrap_x','wrap_y','wrap_z')]==[6,6,6];assert circuit['border_color']['value']==2
for bad in (b'',main_blob[:-1],struct.pack('<Q4I',23,0,0,0,0)):
 try:m.decode_blob(bad)
 except ValueError:pass
 else:raise AssertionError('malformed sampler blob accepted')
try:m.decode_validated_class('DEADBEEF',main_blob)
except ValueError as e:assert 'not validated' in str(e)
else:raise AssertionError('same-sized non-sampler class was decoded')
print('PASS: retail sampler vectors, malformed-size gates, and exact class ownership gate')
