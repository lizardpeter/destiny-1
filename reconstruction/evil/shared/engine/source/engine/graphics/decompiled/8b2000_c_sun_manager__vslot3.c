/* c_sun_manager::vslot3 @ 0x8b2000  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: Clears sun tag handle and state bytes/word at this+0x30..0x34.
 */
typedef struct st_8b2000_0 {
    char padding_0[44];
    unsigned int field_2c;
} st_8b2000_0;


void sub_8b2000(st_8b2000_0 *idx)
{
    idx->field_2c = 0xffffffff;
    idx[1].padding_0[0] = 0;
    idx[1].padding_0[2] = 0;
    *(unsigned int *)&idx[1].padding_0[4] = 0;
    return;
}
