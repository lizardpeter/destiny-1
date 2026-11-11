/* auto_exposure_scaled @ 0x844100  (CUSA00219 01.33)
 * angr 10.0.3 decompiler output, unedited. Machine pseudo-C, NOT reconstructed source.
 * Float arguments passed in XMM registers are sometimes dropped by angr; check the disassembly.
 * Role: returns *(float*)0x18DEEB0 (=0.33, writable) * G[+0xC].
 */

extern char g_18deeb0;

int sub_844100(unsigned long a0)
{
    return &g_18deeb0;
}
