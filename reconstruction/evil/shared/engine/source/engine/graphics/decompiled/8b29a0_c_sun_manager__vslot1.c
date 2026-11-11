/* c_sun_manager::vslot1 @ 0x8b29a0  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Clears sun tag handle (this+0x2c = -1) and flag byte this+0x30.
 */
typedef struct st_8b29a0_0 {
    char padding_0[44];
    unsigned int field_2c;
} st_8b29a0_0;


void sub_8b29a0(st_8b29a0_0 *idx)
{
    idx->field_2c = 0xffffffff;
    idx[1].padding_0[0] = 0;
    return;
}
