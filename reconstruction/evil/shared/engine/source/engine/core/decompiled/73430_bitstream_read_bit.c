
ulong FUN_00073430(long param_1)

{
  uint uVar1;
  byte bVar2;
  uint uVar3;
  ulong uVar4;
  byte *pbVar5;
  byte *pbVar6;
  long lVar7;
  ulong uVar8;
  int iVar9;
  
  uVar4 = *(ulong *)(param_1 + 0x28);
  uVar3 = *(uint *)(param_1 + 0x30);
  if (uVar3 < 0x40) {
    *(ulong *)(param_1 + 0x28) = uVar4 * 2;
    *(uint *)(param_1 + 0x30) = uVar3 + 1;
    *(int *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + 1;
    return uVar4 >> 0x3f;
  }
  pbVar5 = *(byte **)(param_1 + 8);
  pbVar6 = *(byte **)(param_1 + 0x38);
  if (pbVar5 < pbVar6 + 8) {
    if (pbVar6 < pbVar5) {
      iVar9 = ~(uint)pbVar6 + (int)pbVar5;
      uVar8 = 0;
      do {
        bVar2 = *pbVar6;
        pbVar6 = pbVar6 + 1;
        *(byte **)(param_1 + 0x38) = pbVar6;
        uVar8 = uVar8 << 8 | (ulong)bVar2;
      } while (pbVar5 != pbVar6);
      uVar8 = uVar8 << ((char)iVar9 * -8 + 0x38U & 0x3f);
      iVar9 = iVar9 * 8 + 8;
    }
    else {
      uVar8 = 0;
      iVar9 = 0;
    }
  }
  else {
    uVar8 = swap_bytes(*(undefined8 *)pbVar6);
    *(byte **)(param_1 + 0x38) = pbVar6 + 8;
    iVar9 = 0x40;
  }
  *(int *)(param_1 + 0x20) = *(int *)(param_1 + 0x20) + iVar9;
  *(int *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + 1;
  uVar1 = uVar3 - 0x3f;
  lVar7 = 0;
  if (uVar1 < 0x40) {
    lVar7 = uVar8 << ((byte)uVar1 & 0x3f);
  }
  *(long *)(param_1 + 0x28) = lVar7;
  *(uint *)(param_1 + 0x30) = uVar1;
  uVar8 = uVar8 >> (0x7fU - (char)uVar3 & 0x3f);
  return CONCAT71((int7)(uVar8 >> 8),(long)uVar4 < 0 || uVar8 != 0);
}

