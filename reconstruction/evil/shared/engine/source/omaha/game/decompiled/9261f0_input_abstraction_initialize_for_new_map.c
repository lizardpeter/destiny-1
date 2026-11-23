
void FUN_009261f0(void)

{
  undefined4 *puVar1;
  uint uVar2;
  bool bVar3;
  
  puVar1 = (undefined4 *)(PTR_DAT_01a1f5b8 + 0x2b0);
  uVar2 = 0;
  do {
    *puVar1 = 0x25;
    puVar1[5] = 0x25;
    puVar1[10] = 0x25;
    puVar1[0xf] = 0x25;
    puVar1[0x14] = 0x25;
    puVar1[0x19] = 0x25;
    puVar1[0x1e] = 0x25;
    puVar1[0x23] = 0x25;
    puVar1[0x28] = 0x25;
    puVar1[0x2d] = 0x25;
    puVar1[0x32] = 0x25;
    puVar1[0x37] = 0x25;
    puVar1[0x3c] = 0x25;
    puVar1[0x41] = 0x25;
    puVar1[0x46] = 0x25;
    puVar1[0x4b] = 0x25;
    puVar1[0x50] = 0x25;
    puVar1[0x55] = 0x25;
    puVar1[0x5a] = 0x25;
    puVar1[0x5f] = 0x25;
    puVar1[100] = 0x25;
    if (uVar2 == 0xfffffffe) {
      DAT_0273fbe9 = 1;
      return;
    }
    puVar1 = puVar1 + 0xc0;
    bVar3 = uVar2 < 3;
    uVar2 = uVar2 + 1;
  } while (bVar3);
  DAT_0273fbe9 = 1;
  return;
}

