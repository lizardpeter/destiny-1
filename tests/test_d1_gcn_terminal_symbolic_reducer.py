#!/usr/bin/env python3
from __future__ import annotations
import sys,tempfile,unittest
from pathlib import Path

ROOT=Path(__file__).resolve().parents[1]
sys.path.insert(0,str(ROOT/'tools'))
import d1_gcn_terminal_symbolic_reducer as red

class TestTerminalSymbolicReducer(unittest.TestCase):
    def analyze_text(self,text):
        with tempfile.TemporaryDirectory() as td:
            p=Path(td)/'PS_DEADBEEF.s'
            p.write_text(text+'\n')
            return red.analyze('DEADBEEF',p,{'instructions':[]},{'loads':[]})

    def test_initial_vgpr_is_exact_hardware_input_leaf(self):
        d=self.analyze_text('\n'.join([
            '/*000000000000: 00000000 */ v_cmp_lg_i32    vcc, 0, v4',
            '/*000000000004: 00000000 */ v_cndmask_b32   v0, -1.0, 1.0, vcc',
            '/*00000000000c: 00000000 */ v_mov_b32       v1, 0',
            '/*000000000010: 00000000 */ v_cvt_pkrtz_f16_f32 v2, v0, v0',
            '/*000000000014: 00000000 */ v_cvt_pkrtz_f16_f32 v3, v0, v1',
            '/*000000000018: 00000000 */ exp             mrt0, v2, v2, v3, v3 done compr vm',
        ]))
        self.assertTrue(d['exact_terminal_expression'])
        self.assertIn('INPUT_VGPR(v4)',d['terminal_expressions']['R'])
        self.assertEqual(d['terminal_bad_channels'],[])

    def test_unknown_sgpr_still_fails_closed(self):
        d=self.analyze_text('\n'.join([
            '/*000000000000: 00000000 */ v_mov_b32       v0, s9',
            '/*000000000004: 00000000 */ v_mov_b32       v1, 0',
            '/*000000000008: 00000000 */ v_cvt_pkrtz_f16_f32 v2, v0, v0',
            '/*00000000000c: 00000000 */ v_cvt_pkrtz_f16_f32 v3, v0, v1',
            '/*000000000010: 00000000 */ exp             mrt0, v2, v2, v3, v3 done compr vm',
        ]))
        self.assertFalse(d['exact_terminal_expression'])
        self.assertIn('UNKNOWN(',d['terminal_expressions']['R'])
        self.assertIn('R',d['terminal_bad_channels'])

    def test_off_path_unsupported_vector_op_does_not_poison_terminal(self):
        d=self.analyze_text('\n'.join([
            '/*000000000000: 00000000 */ v_cubema_f32    v7, v1, v2, v3',
            '/*000000000008: 00000000 */ v_mov_b32       v0, 1.0',
            '/*00000000000c: 00000000 */ v_mov_b32       v1, 0',
            '/*000000000010: 00000000 */ v_cvt_pkrtz_f16_f32 v2, v0, v0',
            '/*000000000014: 00000000 */ v_cvt_pkrtz_f16_f32 v3, v0, v1',
            '/*000000000018: 00000000 */ exp             mrt0, v2, v2, v3, v3 done compr vm',
        ]))
        self.assertTrue(d['exact_terminal_expression'])
        self.assertEqual(d['terminal_bad_channels'],[])
        self.assertEqual(d['off_path_unsupported_operation_count'],1)
        self.assertEqual(d['unsupported_operations'][0]['mnemonic'],'v_cubema_f32')

if __name__=='__main__':
    unittest.main()
