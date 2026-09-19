#!/usr/bin/env python3
from __future__ import annotations
import sys, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))

import d1_gcn_cbuffer_usage_analyze as cb
import d1_gcn_terminal_alpha_slice as al


class TestGCNProvenance(unittest.TestCase):
    def test_spilled_imm_cbuffer_dword_recovery(self):
        usage={'slots':[
            {'index':0,'usage_name':'PtrExtendedUserData','api_slot':1,'start_register':2},
            {'index':1,'usage_name':'ImmConstBuffer','api_slot':0,'start_register':16},
            {'index':2,'usage_name':'ImmConstBuffer','api_slot':12,'start_register':20},
        ]}
        text='\n'.join([
            '/*000000000000: 00000000 */ s_load_dwordx4  s[4:7], s[2:3], 0x0',
            '/*000000000004: 00000000 */ s_buffer_load_dwordx2 s[8:9], s[4:7], 0x8',
            '/*000000000008: 00000000 */ s_load_dwordx4  s[12:15], s[2:3], 0x4',
            '/*00000000000c: 00000000 */ s_buffer_load_dword s16, s[12:15], 0x1c',
        ])
        d=cb.analyze_shader('DEADBEEF',text,usage)
        self.assertEqual(d['api_slot_read_dwords']['0'],[8,9])
        self.assertEqual(d['api_slot_read_dwords']['12'],[28])
        self.assertEqual(d['unresolved_load_count'],0)

    def test_terminal_compressed_alpha_high_half_slice(self):
        text='\n'.join([
            '/*000000000000: 00000000 */ v_interp_p2_f32 v3, v1, attr1.x',
            '/*000000000004: 00000000 */ image_sample    v2, v[2:5], s[4:11], s[12:15] dmask:8',
            '/*000000000008: 00000000 */ s_buffer_load_dword s4, s[0:3], 0x8',
            '/*00000000000c: 00000000 */ v_mul_f32       v0, v2, s4',
            '/*000000000010: 00000000 */ v_mov_b32       v1, 0',
            '/*000000000014: 00000000 */ v_cvt_pkrtz_f16_f32 v2, v1, v1',
            '/*000000000018: 00000000 */ v_cvt_pkrtz_f16_f32 v0, v1, v0',
            '/*00000000001c: 00000000 */ exp             mrt0, v2, v2, v0, v0 done compr vm',
        ])
        p=ROOT/'tests'/'_tmp_terminal_alpha_test.s'
        try:
            p.write_text(text+'\n')
            image={'instructions':[{
                'address':'000000000004','dmask_channels':'w',
                'resources':[{'texture_index':0}],
            }]}
            cbuf={'loads':[{
                'address':'000000000008','destination':[4],
                'api_slot':0,'dword_indices':[8],
            }]}
            d=al.analyze('DEADBEEF',p,image,cbuf)
            self.assertEqual(d['terminal_packed_ba_register'],'v0')
            self.assertEqual(d['value_slice']['cbuffer_dwords'],{'0':[8]})
            self.assertEqual(d['value_slice']['texture_sample_channels'],[
                {'texture_index':'0','channel':'w'}
            ])
            self.assertEqual(d['value_slice']['unknown_registers'],[])
        finally:
            if p.exists():p.unlink()


if __name__=='__main__':
    unittest.main()
