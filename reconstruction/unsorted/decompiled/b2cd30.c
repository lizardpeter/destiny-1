
ulong FUN_00b2cd30(undefined8 *param_1,long *param_2,int *param_3,int param_4)

{
  int iVar1;
  ulong uVar2;
  undefined8 uVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  uint uVar7;
  
  uVar7 = *(uint *)(param_1 + 2);
  if (uVar7 == 1) {
    if (*(int *)((long)param_1 + 0x14) < 0) {
      uVar2 = thunk_FUN_002e7600(param_1[1],param_2,param_3,param_4);
      return uVar2;
    }
    uVar7 = 0;
    piVar5 = param_3;
    iVar1 = param_4;
    if (0 < param_4) {
      do {
        uVar7 = uVar7 + *piVar5;
        iVar1 = iVar1 + -1;
        piVar5 = piVar5 + 1;
      } while (iVar1 != 0);
    }
    if (*(int *)(param_1 + 3) - *(int *)(param_1 + 4) < (int)uVar7) {
      uVar2 = FUN_00b2cab0(param_1,param_2,param_3,param_4);
      return uVar2;
    }
    if (*(int *)(param_1 + 4) == 0) {
      uVar3 = DAT_026553b0;
      if (DAT_026553a8 == '\0') {
        uVar3 = FUN_000694d0();
      }
      *param_1 = uVar3;
    }
    if (0 < param_4) {
      do {
        if (0 < *param_3) {
          iVar1 = *(int *)(param_1 + 4);
          *(int *)(param_1 + 4) = *param_3 + iVar1;
          iVar6 = (*(int *)((long)param_1 + 0x1c) + iVar1) % *(int *)(param_1 + 3);
          iVar4 = *(int *)(param_1 + 3) - iVar6;
          iVar1 = *param_3;
          if (iVar1 < iVar4) {
            iVar4 = iVar1;
          }
          thunk_FUN_012aa7c6((long)param_1 + (long)iVar6 + 0x24,*param_2,(long)iVar4);
          if (0 < iVar1 - iVar4) {
            thunk_FUN_012aa7c6((long)param_1 + 0x24,*param_2 + (long)iVar4,(long)(iVar1 - iVar4));
          }
        }
        param_2 = param_2 + 1;
        param_3 = param_3 + 1;
        param_4 = param_4 + -1;
      } while (param_4 != 0);
    }
  }
  return (ulong)uVar7;
}

