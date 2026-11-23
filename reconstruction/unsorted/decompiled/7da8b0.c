
long FUN_007da8b0(void)

{
  ulong *puVar1;
  long lVar2;
  ulong uVar3;
  ulong uVar4;
  uint uVar5;
  int iVar6;
  ulong uVar7;
  bool bVar8;
  
  lVar2 = DAT_026df268;
  puVar1 = (ulong *)(DAT_026df268 + 0x28000);
  uVar4 = *(ulong *)(DAT_026df268 + 0x28000);
  do {
    uVar7 = uVar4 >> 0x20;
    iVar6 = (int)(uVar4 >> 0x20);
    uVar5 = iVar6 + 1;
    if (iVar6 == 0x9ff) {
      uVar5 = 0;
    }
    if (uVar5 == (uint)uVar4) {
      return 0;
    }
    LOCK();
    uVar3 = *puVar1;
    if (uVar4 == uVar3) {
      *puVar1 = (ulong)uVar5 << 0x20 | uVar4 & 0xffffffff;
      uVar3 = uVar4;
    }
    UNLOCK();
    bVar8 = uVar3 != uVar4;
    uVar4 = uVar3;
  } while (bVar8);
  return lVar2 + uVar7 * 0x40;
}

