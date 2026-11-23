
void FUN_0100ce30(undefined8 *param_1,long *param_2)

{
  undefined8 *puVar1;
  long lVar2;
  undefined8 uVar3;
  short sVar4;
  long lVar5;
  
  param_1[1] = 0;
  *param_1 = 0;
  *(undefined4 *)param_1 = 0xffffffff;
  *(undefined4 *)(param_1 + 2) = 0xffffffff;
  lVar2 = *param_2;
  sVar4 = (short)param_2[1];
  lVar5 = (long)*(int *)((long)param_2 + 0xc);
  if (lVar5 != -1) {
    if (*(short *)(lVar2 + 0x2bd1e + lVar5 * 4) <= sVar4) {
      param_1[1] = 0;
      *param_1 = 0;
      *(undefined4 *)param_1 = 0xffffffff;
      *(undefined4 *)(param_1 + 2) = 0xffffffff;
      return;
    }
    sVar4 = *(short *)(lVar2 + 0x2a51c +
                      ((long)*(short *)(lVar2 + 0x2bd1c + lVar5 * 4) + (long)sVar4) * 2);
  }
  param_1[1] = 0;
  *param_1 = 0;
  *(undefined4 *)param_1 = 0xffffffff;
  *(undefined4 *)(param_1 + 2) = 0xffffffff;
  if ((sVar4 != -1) && (*(int *)(lVar2 + 0x520 + (long)sVar4 * 0x38) != -1)) {
    puVar1 = (undefined8 *)(lVar2 + 0x520 + (long)sVar4 * 0x38);
    *(undefined4 *)(param_1 + 2) = *(undefined4 *)(puVar1 + 2);
    uVar3 = *puVar1;
    param_1[1] = puVar1[1];
    *param_1 = uVar3;
  }
  return;
}

