#!/usr/bin/env python3
from __future__ import annotations
import sys, unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))

import d1_gcn_cbuffer_usage_analyze as cb
import d1_gcn_terminal_alpha_slice as al
import d1_gcn_terminal_rgb_slice as rgb
import d1_gcn_image_coordinate_slice as coord
import d1_crota_vs_param_vertex_input_lineage as vsin


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
        d=cb.analyze('DEADBEEF',text,usage)
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

    def test_terminal_compressed_rgb_channel_unpack(self):
        text='\n'.join([
            '/*000000000000: 00000000 */ image_sample    v[2:4], v[8:11], s[4:11], s[12:15] dmask:7',
            '/*000000000004: 00000000 */ s_buffer_load_dwordx4 s[4:7], s[0:3], 0x8',
            '/*000000000008: 00000000 */ v_mul_f32       v2, v2, s4',
            '/*00000000000c: 00000000 */ v_mul_f32       v3, v3, s5',
            '/*000000000010: 00000000 */ v_mul_f32       v4, v4, s6',
            '/*000000000014: 00000000 */ v_mov_b32       v5, 0',
            '/*000000000018: 00000000 */ v_cvt_pkrtz_f16_f32 v6, v2, v3',
            '/*00000000001c: 00000000 */ v_cvt_pkrtz_f16_f32 v7, v4, v5',
            '/*000000000020: 00000000 */ exp             mrt0, v6, v6, v7, v7 done compr vm',
        ])
        p=ROOT/'tests'/'_tmp_terminal_rgb_test.s'
        try:
            p.write_text(text+'\n')
            image={'instructions':[{
                'address':'000000000000','dmask_channels':'xyz',
                'resources':[{'texture_index':3}],
            }]}
            cbuf={'loads':[{
                'address':'000000000004','destination':[4,5,6,7],
                'api_slot':0,'dword_indices':[8,9,10,11],
            }]}
            d=rgb.analyze('DEADBEEF',p,image,cbuf)
            self.assertEqual(d['terminal_packed_rg_register'],'v6')
            self.assertEqual(d['terminal_packed_ba_register'],'v7')
            for ch,texch,dw in [('R','x',8),('G','y',9),('B','z',10)]:
                s=d['channels'][ch]['value_slice']
                self.assertEqual(s['texture_sample_channels'],[
                    {'texture_index':'3','channel':texch}
                ])
                self.assertEqual(s['cbuffer_dwords'],{'0':[dw]})
                self.assertEqual(s['unknown_registers'],[])
        finally:
            if p.exists():p.unlink()

    def test_image_coordinate_snapshot_precedes_sample_destination_overwrite(self):
        text='\n'.join([
            '/*000000000000: 00000000 */ v_interp_p2_f32 v2, v1, attr1.x',
            '/*000000000004: 00000000 */ v_mov_b32       v3, 0',
            '/*000000000008: 00000000 */ image_sample    v[2:3], v[2:5], s[4:11], s[12:15] dmask:3',
            '/*00000000000c: 00000000 */ v_mul_f32       v4, v2, 2.0',
            '/*000000000010: 00000000 */ image_sample    v5, v[4:7], s[16:23], s[24:27] dmask:1',
        ])
        p=ROOT/'tests'/'_tmp_image_coordinate_test.s'
        try:
            p.write_text(text+'\n')
            image={
                'image_instruction_count':2,
                'instructions':[
                    {
                        'address':'000000000008','dmask_channels':'xy',
                        'resources':[{'texture_index':0}],
                        'samplers':[{'sampler_index':1}],
                    },
                    {
                        'address':'000000000010','dmask_channels':'x',
                        'resources':[{'texture_index':2}],
                        'samplers':[{'sampler_index':3}],
                    },
                ],
            }
            d=coord.analyze('DEADBEEF',p,image,{'loads':[]})
            self.assertEqual(d['sample_count'],2)
            first,second=d['samples']
            self.assertEqual(first['encoded_coordinate_registers'],['v2','v3','v4','v5'])
            self.assertIn('attr1.x',first['coordinate_sources']['interpolants'])
            self.assertEqual(
                second['coordinate_sources']['prior_texture_sample_channels'],
                [{'texture_index':0,'channel':'x','sample_address':'000000000008'}]
            )
            self.assertEqual((second['texture_index'],second['sampler_index']),(2,3))
        finally:
            if p.exists():p.unlink()

    def test_vs_param_slice_preserves_initial_gnm_vertex_input_vgprs(self):
        text='\n'.join([
            '/*000000000000: 00000000 */ v_mul_f32       v8, v2, 2.0',
            '/*000000000004: 00000000 */ v_add_f32       v9, v3, 1.0',
            '/*000000000008: 00000000 */ exp             param1, v8, v9, v9, v9',
        ])
        p=ROOT/'tests'/'_tmp_vs_param_input_test.s'
        header={
            'vertex_input_semantics':[
                {'index':0,'semantic':17,'vgpr':2,'size_in_elements':2,'raw_hex':'11020200'},
            ],
        }
        try:
            p.write_text(text+'\n')
            d=vsin.analyze('DEADBEEF',p,header,1)
            self.assertEqual(d['x']['vertex_input_semantic_ids'],[17])
            self.assertEqual(d['y']['vertex_input_semantic_ids'],[17])
            self.assertEqual(
                [(x['register'],x['element_index']) for x in d['xy']['vertex_input_leaves']],
                [('v2',0),('v3',1)]
            )
            self.assertEqual(d['xy']['unknown_vgpr_leaves'],[])
        finally:
            if p.exists():p.unlink()


if __name__=='__main__':
    unittest.main()
