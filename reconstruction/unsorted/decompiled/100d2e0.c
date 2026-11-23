
void FUN_0100d2e0(long param_1,int *param_2)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  int *piVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  int iVar8;
  
  piVar3 = (int *)(param_1 + -8);
  iVar8 = 0;
  do {
    iVar7 = iVar8;
    piVar4 = piVar3;
    if (*(int *)(param_1 + 8) <= iVar7) {
      return;
    }
    iVar8 = iVar7 + 1;
    piVar3 = piVar4 + 5;
  } while (piVar4[7] != *param_2);
  if (iVar8 != 0) {
    iVar6 = *piVar3;
    if (0 < iVar6) {
      FUN_0100d400(param_1 + 0x2a518,(int)(short)piVar4[6],
                   (int)(short)((short)iVar6 + -1 + (short)piVar4[6]));
      iVar6 = *piVar3;
    }
    iVar5 = piVar4[6] + iVar6;
    iVar2 = *(int *)(param_1 + 0x510);
    iVar1 = iVar2 - iVar5;
    if (0 < iVar1) {
      thunk_FUN_012aaab6(param_1 + 0x518 + (long)piVar4[6] * 0x38,
                         param_1 + 0x518 + (long)iVar5 * 0x38,(long)iVar1 * 0x38);
      iVar2 = *(int *)(param_1 + 0x510);
    }
    *(int *)(param_1 + 0x510) = iVar2 - iVar6;
    iVar2 = *(int *)(param_1 + 8);
    if (0 < iVar2 - iVar8) {
      thunk_FUN_012aaab6(piVar3,piVar4 + 10,(long)(iVar2 - iVar8) * 0x14);
      iVar2 = *(int *)(param_1 + 8);
    }
    iVar2 = iVar2 + -1;
    *(int *)(param_1 + 8) = iVar2;
    if (0 < iVar2) {
      piVar3 = (int *)(param_1 + 0x10);
      iVar8 = 0;
      do {
        if (iVar7 <= iVar8) {
          *piVar3 = *piVar3 - iVar6;
          iVar2 = *(int *)(param_1 + 8);
        }
        piVar3 = piVar3 + 5;
        iVar8 = iVar8 + 1;
      } while (iVar8 < iVar2);
    }
  }
  return;
}

