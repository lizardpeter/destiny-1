
undefined8 FUN_009cdc10(long param_1,undefined8 *param_2,long *param_3)

{
  short *psVar1;
  short *psVar2;
  int iVar3;
  
  psVar1 = (short *)*param_2;
  psVar2 = (short *)param_2[1];
  if (psVar1 == psVar2) {
    return 0;
  }
  if (*psVar1 == 2) {
    if (psVar1 + 2 != psVar2) {
      return 0;
    }
    if ((((undefined *)*param_3 == PTR_DAT_01a1f5f8) ||
        ((undefined *)param_3[1] == PTR_DAT_01a1f630)) ||
       (iVar3 = 0, (undefined *)param_3[1] == PTR_DAT_01a1f5f8)) {
      iVar3 = (int)param_3[5];
    }
    if (*(int *)(param_1 + 0x28c) == iVar3) {
      return 1;
    }
    if (psVar1[1] != 0) {
      return 0;
    }
    if ((((undefined *)*param_3 != PTR_DAT_01a1f5f8) &&
        ((undefined *)param_3[1] != PTR_DAT_01a1f630)) &&
       ((undefined *)param_3[1] != PTR_DAT_01a1f5f8)) {
      return 0;
    }
    *(int *)(param_1 + 0x28c) = (int)param_3[5];
  }
  else {
    if (*psVar1 != 0) {
      return 0;
    }
    if (psVar1 + 2 != psVar2) {
      return 0;
    }
    if ((((undefined *)*param_3 == PTR_DAT_01a1f5f8) ||
        ((undefined *)param_3[1] == PTR_DAT_01a1f630)) ||
       (iVar3 = 0, (undefined *)param_3[1] == PTR_DAT_01a1f5f8)) {
      iVar3 = (int)param_3[5];
    }
    if (*(int *)(param_1 + 0x288) == iVar3) {
      return 1;
    }
    if (psVar1[1] != 0) {
      return 0;
    }
    if ((((undefined *)*param_3 != PTR_DAT_01a1f5f8) &&
        ((undefined *)param_3[1] != PTR_DAT_01a1f630)) &&
       ((undefined *)param_3[1] != PTR_DAT_01a1f5f8)) {
      return 0;
    }
    *(int *)(param_1 + 0x288) = (int)param_3[5];
  }
  FUN_009984d0(param_1 + 0x78,0xffffffff);
  return 1;
}

