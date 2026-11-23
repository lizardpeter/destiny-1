
undefined8 FUN_0054cab0(undefined8 param_1,uint param_2)

{
  char cVar1;
  int iVar2;
  int iVar3;
  int *piVar4;
  int *piVar5;
  undefined8 uVar6;
  undefined4 *puVar7;
  short sVar8;
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar1 = FUN_0025cc10();
  sVar8 = -1;
  if ((cVar1 != '\0') && (*DAT_026b9590 != -1)) {
    iVar2 = FUN_00338340((ulong)((param_2 & 0x1fff) * DAT_02692230) + DAT_02692228);
    piVar4 = (int *)FUN_0054c7f0(param_1);
    if ((piVar4 != (int *)0x0) && (0 < *piVar4)) {
      sVar8 = 0;
      do {
        piVar5 = (int *)FUN_0054c7f0(param_1);
        if (((ulong)(long)sVar8 < (ulong)(long)*piVar5) &&
           (puVar7 = (undefined4 *)
                     ((long)piVar5 + (long)sVar8 * 0x20 + *(long *)(piVar5 + 2) + 0x18),
           puVar7 != (undefined4 *)0x0)) {
          uVar6 = FUN_0033fa20();
          local_40[0] = *puVar7;
          iVar3 = FUN_0033fc20(uVar6,local_40);
          if ((iVar3 != -1) && (iVar2 == iVar3)) goto LAB_0054cb9f;
        }
        sVar8 = sVar8 + 1;
      } while ((int)sVar8 < *piVar4);
      sVar8 = -1;
    }
  }
LAB_0054cb9f:
  if (*DAT_01a1f100 != local_38) {
    uVar6 = thunk_FUN_012aa7f6();
    return uVar6;
  }
  return CONCAT62((int6)((ulong)*DAT_01a1f100 >> 0x10),sVar8);
}

