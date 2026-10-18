
undefined8 FUN_003a25f0(undefined8 *param_1,undefined4 param_2,uint param_3,uint *param_4)

{
  int iVar1;
  uint uVar2;
  uint *puVar3;
  long lVar4;
  undefined8 uVar5;
  ulong uVar6;
  long lVar7;
  uint uVar8;
  long lVar9;
  uint local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  param_1[7] = 0;
  param_1[6] = 0;
  param_1[5] = 0;
  param_1[4] = 0;
  param_1[3] = 0;
  param_1[2] = 0;
  param_1[1] = 0;
  *param_1 = 0;
  *(undefined4 *)param_1 = 0xffffffff;
  *(undefined4 *)((long)param_1 + 4) = 0xffffffff;
  *(undefined2 *)((long)param_1 + 10) = 0xffff;
  *(undefined4 *)((long)param_1 + 0xc) = 0x811c9dc5;
  *(undefined4 *)(param_1 + 2) = 0xffffffff;
  *(undefined4 *)((long)param_1 + 0x14) = 0xffffffff;
  *(undefined4 *)(param_1 + 3) = 0xffffffff;
  *(undefined8 *)((long)param_1 + 0x1c) = 0xff7fffff3f800000;
  *(undefined4 *)((long)param_1 + 0x24) = 0xff7fffff;
  *(undefined4 *)(param_1 + 5) = 0xff7fffff;
  *(undefined4 *)((long)param_1 + 0x2c) = 0xff7fffff;
  if ((*param_4 != 0x811c9dc5) && (param_3 != 0xffffffff)) {
    *(undefined4 *)param_1 = param_2;
    *(uint *)((long)param_1 + 4) = param_3;
    uVar6 = (ulong)((param_3 & 0x1fff) * DAT_02689800);
    puVar3 = (uint *)FUN_0048ead0((DAT_026897f8 + uVar6) -
                                  ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar6)));
    if (puVar3 != (uint *)0x0) {
      local_40[0] = *param_4;
      iVar1 = FUN_004bb850(puVar3,local_40,0);
      if (iVar1 != -1) {
        uVar2 = (int)*puVar3 >> 0xd;
        lVar4 = *DAT_01a238a0;
        lVar7 = (ulong)((uVar2 >> 0x12 | 0x3ff) & uVar2) * 0x40;
        lVar9 = *(long *)(lVar4 + 0x10 + lVar7);
        uVar6 = (ulong)((*puVar3 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar7));
        uVar2 = *(uint *)(*(long *)(puVar3 + 2) + 0x90 +
                         ((lVar9 + uVar6) -
                         ((long)*(int *)(lVar4 + 0x34 + lVar7) & *(ulong *)(lVar9 + 8 + uVar6))));
        uVar8 = (int)uVar2 >> 0xd;
        lVar7 = (ulong)((uVar8 >> 0x12 | 0x3ff) & uVar8) * 0x40;
        lVar9 = *(long *)(lVar4 + 0x10 + lVar7);
        uVar6 = (ulong)((uVar2 & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar7));
        lVar9 = (lVar9 + uVar6) -
                ((long)*(int *)(lVar4 + 0x34 + lVar7) & *(ulong *)(lVar9 + 8 + uVar6));
        lVar4 = FUN_00491090(lVar9,iVar1);
        if ((-1 < *(short *)(lVar4 + 0x18)) && ((int)*(char *)(lVar4 + 0x1a) - 1U < 2)) {
          FUN_001ceab0(param_1 + 2,0xffffffff,0xffffffff,iVar1);
          *(undefined4 *)(param_1 + 4) = *(undefined4 *)(lVar4 + 0x14);
          *(undefined2 *)((long)param_1 + 10) = *(undefined2 *)(lVar4 + 0x18);
          *(uint *)((long)param_1 + 0xc) = *param_4;
          *(undefined1 *)((long)param_1 + 9) = *(undefined1 *)(lVar4 + 0x1a);
          uVar5 = FUN_00490dd0(lVar9);
          *(undefined4 *)((long)param_1 + 0x24) = 0;
          *(undefined4 *)(param_1 + 5) = 0;
          *(undefined4 *)((long)param_1 + 0x2c) = 0;
          *(undefined4 *)((long)param_1 + 0x1c) = 0x3f800000;
          FUN_003ab8f0(param_1 + 6,uVar5);
          uVar5 = 1;
          goto LAB_003a28bf;
        }
      }
    }
  }
  param_1[7] = 0;
  param_1[6] = 0;
  param_1[5] = 0;
  param_1[4] = 0;
  param_1[3] = 0;
  param_1[2] = 0;
  param_1[1] = 0;
  *param_1 = 0;
  *(undefined4 *)param_1 = 0xffffffff;
  *(undefined4 *)((long)param_1 + 4) = 0xffffffff;
  *(undefined2 *)((long)param_1 + 10) = 0xffff;
  *(undefined8 *)((long)param_1 + 0xc) = 0xffffffff811c9dc5;
  *(undefined4 *)((long)param_1 + 0x14) = 0xffffffff;
  uVar5 = 0;
  *(undefined4 *)(param_1 + 3) = 0xffffffff;
  *(undefined4 *)((long)param_1 + 0x1c) = 0x3f800000;
  *(undefined4 *)(param_1 + 4) = 0xff7fffff;
  *(undefined4 *)((long)param_1 + 0x24) = 0xff7fffff;
  *(undefined4 *)(param_1 + 5) = 0xff7fffff;
  *(undefined4 *)((long)param_1 + 0x2c) = 0xff7fffff;
LAB_003a28bf:
  if (*DAT_01a1f100 == local_38) {
    return uVar5;
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

