
undefined8 FUN_0100d5e0(long param_1,int *param_2,long param_3,undefined8 *param_4)

{
  int iVar1;
  int iVar2;
  long lVar3;
  long *plVar4;
  int *piVar5;
  undefined8 uVar6;
  undefined4 *puVar7;
  int iVar8;
  long lVar9;
  uint uVar10;
  ulong uVar11;
  
  plVar4 = DAT_01a1f100;
  lVar3 = *DAT_01a1f100;
  piVar5 = (int *)(param_1 + 0x14);
  iVar1 = *(int *)(param_1 + 8);
  lVar9 = (long)iVar1;
  uVar11 = *(ulong *)(param_3 + 8);
  iVar8 = 0;
  do {
    if (iVar1 <= iVar8) goto LAB_0100d630;
    iVar8 = iVar8 + 1;
    iVar2 = *piVar5;
    piVar5 = piVar5 + 5;
  } while (iVar2 != *param_2);
  uVar6 = 1;
  if (iVar8 == 0) {
LAB_0100d630:
    uVar6 = 2;
    if ((iVar1 != 0x40) && (iVar8 = (int)uVar11, *(int *)(param_1 + 0x510) + iVar8 < 0xc01)) {
      *(int *)(param_1 + 8) = iVar1 + 1;
      *(int *)(param_1 + 0xc + lVar9 * 0x14) = iVar8;
      *(undefined4 *)(param_1 + 0x10 + lVar9 * 0x14) = *(undefined4 *)(param_1 + 0x510);
      piVar5 = (int *)(param_1 + 0x10 + lVar9 * 0x14);
      if (iVar8 < 1) {
        *(int *)(param_1 + 0x14 + lVar9 * 0x14) = *param_2;
        *(undefined8 *)(param_1 + 0x18 + lVar9 * 0x14) = *param_4;
      }
      else {
        *(int *)(param_1 + 0x510) = *(int *)(param_1 + 0x510) + iVar8;
        *(int *)(param_1 + 0x14 + lVar9 * 0x14) = *param_2;
        *(undefined8 *)(param_1 + 0x18 + lVar9 * 0x14) = *param_4;
        lVar9 = 0x10;
        puVar7 = (undefined4 *)((long)*piVar5 * 0x38 + 0x548 + param_1);
        do {
          puVar7[-0xc] = (int)*(char *)(param_3 + 0x10 + lVar9 + *(long *)(param_3 + 0x10));
          puVar7[-10] = 0xffffffff;
          puVar7[-7] = 0;
          *(undefined8 *)(puVar7 + -9) = 0;
          lVar9 = lVar9 + 0x10;
          uVar10 = (int)uVar11 - 1;
          uVar11 = (ulong)uVar10;
          puVar7[-6] = 0xffffffff;
          puVar7[-4] = 0xffffffff;
          puVar7[-1] = 0;
          *(undefined8 *)(puVar7 + -3) = 0;
          *puVar7 = 0xffffffff;
          puVar7 = puVar7 + 0xe;
        } while (uVar10 != 0);
      }
      FUN_0100d750(param_1 + 0x2a518,param_3,(int)(short)*piVar5);
      uVar6 = 0;
    }
  }
  if (*plVar4 != lVar3) {
    uVar6 = thunk_FUN_012aa7f6();
    return uVar6;
  }
  return uVar6;
}

