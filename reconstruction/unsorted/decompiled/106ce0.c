
void FUN_00106ce0(void)

{
  long lVar1;
  
  if ((ulong)DAT_025d6ff8 != 0) {
    lVar1 = *(long *)(&DAT_01ad5030 + (ulong)DAT_025d6ff8 * DAT_01ad5010 + DAT_01ad5000);
    if (lVar1 != 0) {
      *(undefined4 *)(lVar1 + 8) = 0;
      *(undefined4 *)(lVar1 + 0x510) = 0;
      *(undefined4 *)(lVar1 + 0x2a518) = 0;
      thunk_FUN_012aa986(lVar1 + 0x2bd1c,0,0x100);
    }
  }
  return;
}

