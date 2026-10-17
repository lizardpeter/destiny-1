
undefined8 FUN_00b31830(long param_1,long param_2,undefined4 *param_3)

{
  int iVar1;
  uint uVar2;
  int *piVar3;
  ulong uVar4;
  undefined8 uVar5;
  int iVar6;
  int iVar7;
  ulong uVar8;
  int iVar9;
  int local_38 [8];
  long local_18;
  
  local_18 = *DAT_01a1f100;
  local_38[0] = 0;
  local_38[1] = 0;
  local_38[2] = 0;
  local_38[3] = 0;
  local_38[4] = 0;
  iVar1 = *(int *)(param_2 + 0x90);
  if (iVar1 != 0) {
    uVar2 = *(uint *)(param_2 + 0x8c);
    uVar8 = (ulong)uVar2;
    if (uVar2 != 0xffffffff) {
      iVar7 = *(int *)(param_2 + 0x88);
      do {
        iVar6 = (int)uVar8;
        local_38[**(int **)(param_2 + 0x98 + (long)iVar6 * 8)] =
             local_38[**(int **)(param_2 + 0x98 + (long)iVar6 * 8)] + 1;
        iVar9 = (int)((iVar7 - uVar2) + iVar6) % iVar7;
        if ((iVar9 < 0) || (iVar1 + -1 <= iVar9)) break;
        uVar4 = (long)(iVar6 + 1) % (long)iVar7;
        uVar8 = uVar4 & 0xffffffff;
      } while ((int)uVar4 != -1);
      if ((local_38[2] != 0) || (iVar1 == 0)) goto LAB_00b31928;
    }
    uVar8 = (ulong)*(uint *)(param_2 + 0x8c);
    if (*(uint *)(param_2 + 0x8c) != 0xffffffff) {
      while( true ) {
        iVar7 = (int)uVar8;
        piVar3 = *(int **)(param_2 + 0x98 + (long)iVar7 * 8);
        if (*piVar3 == 1) break;
        if (iVar7 == -1) goto LAB_00b31928;
        iVar6 = *(int *)(param_2 + 0x88);
        iVar9 = ((iVar7 - *(int *)(param_2 + 0x8c)) + iVar6) % iVar6;
        if (((iVar9 < 0) || (iVar1 + -1 <= iVar9)) ||
           (uVar4 = (long)(iVar7 + 1) % (long)iVar6, uVar8 = uVar4 & 0xffffffff, (int)uVar4 == -1))
        goto LAB_00b31928;
      }
      *piVar3 = 2;
      *(int **)(param_1 + 0x16c0) = piVar3;
      *(undefined4 *)(param_1 + 0x16a8) = 1;
    }
  }
LAB_00b31928:
  *param_3 = 0;
  if (*DAT_01a1f100 != local_18) {
    uVar5 = thunk_FUN_012aa7f6();
    return uVar5;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
}

