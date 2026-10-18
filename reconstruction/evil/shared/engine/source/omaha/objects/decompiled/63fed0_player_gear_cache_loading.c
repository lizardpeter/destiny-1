
ulong FUN_0063fed0(undefined4 param_1)

{
  ulong *puVar1;
  long *plVar2;
  undefined8 *puVar3;
  int *piVar4;
  ulong uVar5;
  int local_28 [2];
  ulong local_20;
  
  puVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  local_28[0] = FUN_0023e310(&DAT_026bea78);
  if ((local_28[0] == 0) || (plVar2 = (long *)FUN_0023dfa0(local_28), *plVar2 == 0)) {
    uVar5 = *puVar1;
    if (uVar5 != local_20) {
LAB_0063ff4a:
      uVar5 = thunk_FUN_012aa7f6();
      return uVar5;
    }
    uVar5 = uVar5 & 0xffffffffffffff00;
  }
  else {
    puVar3 = (undefined8 *)FUN_0023dfa0(local_28);
    piVar4 = (int *)FUN_0063bef0(*puVar3,param_1);
    uVar5 = (ulong)CONCAT31((int3)(*piVar4 - 6U >> 8),1 < *piVar4 - 6U);
    if (*puVar1 != local_20) goto LAB_0063ff4a;
  }
  return uVar5;
}

