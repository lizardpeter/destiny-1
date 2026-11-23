
void FUN_00072400(undefined8 *param_1)

{
  byte bVar1;
  byte *pbVar2;
  ulong uVar3;
  long lVar4;
  byte *pbVar5;
  int iVar6;
  
  *(undefined4 *)(param_1 + 3) = 3;
  *(undefined4 *)(param_1 + 4) = 0;
  *(undefined4 *)((long)param_1 + 0x24) = 0;
  *(undefined4 *)(param_1 + 8) = 0;
  *(undefined1 *)((long)param_1 + 0x1c) = 0;
  pbVar5 = (byte *)*param_1;
  param_1[7] = pbVar5;
  param_1[5] = 0;
  *(undefined4 *)(param_1 + 6) = 0;
  pbVar2 = (byte *)param_1[1];
  if (pbVar2 < pbVar5 + 8) {
    if (pbVar5 < pbVar2) {
      iVar6 = ~(uint)pbVar5 + (int)pbVar2;
      uVar3 = 0;
      do {
        bVar1 = *pbVar5;
        pbVar5 = pbVar5 + 1;
        param_1[7] = pbVar5;
        uVar3 = uVar3 << 8 | (ulong)bVar1;
      } while (pbVar2 != pbVar5);
      lVar4 = uVar3 << ((char)iVar6 * -8 + 0x38U & 0x3f);
      iVar6 = iVar6 * 8 + 8;
    }
    else {
      lVar4 = 0;
      iVar6 = 0;
    }
  }
  else {
    lVar4 = swap_bytes(*(undefined8 *)pbVar5);
    param_1[7] = pbVar5 + 8;
    iVar6 = 0x40;
  }
  *(int *)(param_1 + 4) = iVar6;
  param_1[5] = lVar4;
  return;
}

