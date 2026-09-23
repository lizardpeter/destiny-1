import struct
import unittest

from tools.d1_material_render_state import decode_material_render_state


def payload(state16: int) -> bytes:
    b = bytearray(0x330)
    struct.pack_into('<Q', b, 0, len(b))
    struct.pack_into('<H', b, 0x20, state16)
    struct.pack_into('<I', b, 0x28, 0x80ABCDEF)
    struct.pack_into('<I', b, 0x2A8, 0x80123456)
    return bytes(b)


class TestD1MaterialRenderState(unittest.TestCase):
    def test_opaque_zero_state(self):
        d = decode_material_render_state(payload(0x0000))
        self.assertFalse(d['transparent_draw_population'])
        self.assertEqual(d['portable_alpha_class'], 'OPAQUE')
        self.assertFalse(d['exact_blend_state_known'])
        self.assertEqual(d['state4_hex'], '00000000')
        self.assertEqual(d['state4_lanes_u8'], [0, 0, 0, 0])

    def test_known_state8_selector(self):
        d = decode_material_render_state(payload(0x0088))
        self.assertTrue(d['transparent_draw_population'])
        self.assertEqual(d['portable_alpha_class'], 'BLEND')
        self.assertEqual(d['unk20_low_hex'], '0x88')
        self.assertTrue(d['exact_blend_state_known'])
        self.assertEqual(d['exact_blend_state_index'], 8)
        self.assertEqual(d['exact_blend_equation'], 'Source + Destination*(1-SourceAlpha)')
        self.assertEqual(d['state4_hex'], '88000000')
        self.assertEqual(d['state4_selector_syntax'][0]['selected_low7_if_highbit_set'], 8)

    def test_unknown_nonzero_state_is_not_overclaimed(self):
        d = decode_material_render_state(payload(0x0042))
        self.assertTrue(d['transparent_draw_population'])
        self.assertEqual(d['portable_alpha_class'], 'BLEND')
        self.assertFalse(d['exact_blend_state_known'])
        self.assertIsNone(d['exact_blend_state_index'])
        self.assertIsNone(d['exact_blend_equation'])

    def test_full_state4_preserved_without_lane_semantic_promotion(self):
        b = bytearray(payload(0x0088))
        b[0x22] = 0x81
        b[0x23] = 0x84
        d = decode_material_render_state(bytes(b))
        self.assertEqual(d['state4_hex'], '88008184')
        self.assertEqual(d['state4_lanes_u8'], [0x88, 0x00, 0x81, 0x84])
        self.assertEqual(
            [x['selected_low7_if_highbit_set'] for x in d['state4_selector_syntax']],
            [8, None, 1, 4],
        )
        self.assertTrue(d['proof']['full_state4_bytes_preserved_exactly'])
        self.assertFalse(d['proof']['state4_lanes_1_3_semantics_promoted_here'])


if __name__ == '__main__':
    unittest.main()
