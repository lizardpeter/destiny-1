
ulong FUN_003454c0(long param_1,undefined4 param_2)

{
  int *piVar1;
  long *plVar2;
  char cVar3;
  byte bVar4;
  int iVar5;
  ulong uVar6;
  undefined4 local_30 [2];
  long local_28;
  
  plVar2 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  piVar1 = *(int **)(param_1 + 8);
  uVar6 = 5;
  local_30[0] = param_2;
  if ((((*piVar1 != -1) && (iVar5 = FUN_00057e60(local_30), -1 < iVar5)) &&
      (iVar5 = FUN_00057e60(local_30), iVar5 < 0x200)) &&
     (iVar5 = FUN_00057e60(local_30), piVar1[(long)iVar5 * 4 + 4] != -1)) {
    cVar3 = FUN_0012d770(piVar1 + 0x857,local_30[0]);
    uVar6 = 6;
    if (cVar3 == '\0') {
      cVar3 = FUN_0012d770(piVar1 + 0x867,local_30[0]);
      uVar6 = 7;
      if (cVar3 == '\0') {
        cVar3 = FUN_000f93a0(piVar1 + 0x845,local_30);
        uVar6 = 4;
        if (cVar3 == '\0') {
          cVar3 = FUN_000f93a0(piVar1 + 0x846,local_30);
          uVar6 = 2;
          if (cVar3 == '\0') {
            bVar4 = FUN_0012d770(piVar1 + 0x847,local_30[0]);
            if (*plVar2 == local_28) {
              return (ulong)(bVar4 + 1 + (uint)bVar4);
            }
            goto LAB_003455cc;
          }
        }
      }
    }
  }
  if (*plVar2 == local_28) {
    return uVar6;
  }
LAB_003455cc:
  uVar6 = thunk_FUN_012aa7f6();
  return uVar6;
}

