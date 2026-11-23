
uint FUN_00303ba0(void)

{
  char cVar1;
  uint uVar2;
  uint uVar3;
  
  uVar2 = FUN_002400b0();
  uVar3 = 0xffffffff;
  if (uVar2 != 0xffffffff) {
    cVar1 = FUN_0006eeb0(&DAT_02689580,uVar2 & 0xffff);
    if (((short)uVar2 != -1) && (cVar1 == '\x01')) {
      uVar3 = (uint)(DAT_026895a0 >> 0x20) &
              *(uint *)(DAT_02689588 +
                       (ulong)DAT_0268959c + (DAT_026895a0 & 0xffffffff) * (ulong)(uVar2 & 0xffff));
      if ((DAT_026895b4 & 0x40000000) == 0) {
        uVar3 = (uVar3 & 0xff) << 0x17 | (DAT_026895b4 & 0x3ff) << 0xd | uVar2 & 0x1fff;
      }
      else {
        uVar3 = (uVar3 & 7) << 0x1b | (DAT_026895b4 & 0x3fff) << 0xd | uVar2 & 0x1fff | 0x80000000;
      }
    }
  }
  return uVar3;
}

