
ulong FUN_00072c70(long param_1,int param_2)

{
  uint uVar1;
  byte bVar2;
  int iVar3;
  ulong uVar4;
  byte *pbVar5;
  ulong uVar6;
  byte *pbVar7;
  long lVar8;
  byte bVar9;
  int iVar10;
  
  iVar3 = *(int *)(param_1 + 0x30);
  uVar4 = *(ulong *)(param_1 + 0x28);
  bVar9 = (byte)param_2;
  if (0x40 - iVar3 < param_2) {
    pbVar5 = *(byte **)(param_1 + 8);
    pbVar7 = *(byte **)(param_1 + 0x38);
    if (pbVar5 < pbVar7 + 8) {
      if (pbVar7 < pbVar5) {
        iVar10 = ~(uint)pbVar7 + (int)pbVar5;
        uVar6 = 0;
        do {
          bVar2 = *pbVar7;
          pbVar7 = pbVar7 + 1;
          *(byte **)(param_1 + 0x38) = pbVar7;
          uVar6 = uVar6 << 8 | (ulong)bVar2;
        } while (pbVar5 != pbVar7);
        uVar6 = uVar6 << ((char)iVar10 * -8 + 0x38U & 0x3f);
        iVar10 = iVar10 * 8 + 8;
      }
      else {
        uVar6 = 0;
        iVar10 = 0;
      }
    }
    else {
      uVar6 = swap_bytes(*(undefined8 *)pbVar7);
      *(byte **)(param_1 + 0x38) = pbVar7 + 8;
      iVar10 = 0x40;
    }
    *(int *)(param_1 + 0x20) = *(int *)(param_1 + 0x20) + iVar10;
    *(int *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + param_2;
    uVar1 = param_2 + -0x40 + iVar3;
    lVar8 = 0;
    if (uVar1 < 0x40) {
      lVar8 = uVar6 << ((byte)uVar1 & 0x3f);
    }
    *(long *)(param_1 + 0x28) = lVar8;
    *(uint *)(param_1 + 0x30) = uVar1;
    return uVar6 >> (0x40 - (byte)uVar1 & 0x3f) | uVar4 >> (0x40 - bVar9 & 0x3f);
  }
  *(int *)(param_1 + 0x24) = *(int *)(param_1 + 0x24) + param_2;
  *(ulong *)(param_1 + 0x28) = uVar4 << (bVar9 & 0x3f);
  *(int *)(param_1 + 0x30) = iVar3 + param_2;
  return uVar4 >> (0x40 - bVar9 & 0x3f);
}

