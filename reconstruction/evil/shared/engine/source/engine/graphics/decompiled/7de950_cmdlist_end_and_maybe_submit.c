
void FUN_007de950(long *param_1)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  byte bVar4;
  
  piVar3 = (int *)param_1[10];
  if ((((int)*(long *)(piVar3 + 4) - *piVar3 & 0xfffffffcU) == 0) &&
     ((piVar3[0x24] - piVar3[0x20] & 0xfffffffcU) == 0)) {
    bVar4 = 1;
  }
  else {
    if ((ulong)(*(long *)(piVar3 + 2) - *(long *)(piVar3 + 4)) < 0x18) {
      FUN_00f7feb0(piVar3,0x18,2);
      piVar3 = (int *)param_1[10];
    }
    FUN_007ef3a0(&DAT_026e4840,DAT_026df291 ^ 1,*(undefined4 *)(param_1[0xb] + 0x1c),param_1[0xb],
                 piVar3);
    iVar2 = *(int *)(*param_1 + 0xbc);
    iVar1 = *DAT_026e4860;
    FUN_007db810(param_1[0xb],param_1[10],3,0x18,1);
    *(undefined8 *)param_1[10] = ((undefined8 *)param_1[10])[2];
    bVar4 = (byte)((uint)(iVar1 - iVar2) >> 0x1f);
    *(undefined8 *)(param_1[10] + 0x80) = *(undefined8 *)(param_1[10] + 0x90);
  }
  piVar3 = (int *)(param_1[0xb] + 0x18);
  do {
    iVar1 = *piVar3;
    LOCK();
    iVar2 = *piVar3;
    if (iVar1 == iVar2) {
      *piVar3 = 1;
      iVar2 = iVar1;
    }
    UNLOCK();
  } while (iVar1 != iVar2);
  param_1[10] = 0;
  param_1[0xb] = 0;
  if (DAT_018dcc30 != '\0' && bVar4 == 0) {
    FUN_007dd060(param_1);
    return;
  }
  return;
}

