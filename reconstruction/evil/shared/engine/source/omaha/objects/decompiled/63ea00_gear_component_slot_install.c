
void FUN_0063ea00(char *param_1,undefined4 param_2,undefined8 param_3,undefined8 param_4,int param_5
                 ,int *param_6)

{
  char cVar1;
  undefined4 uVar2;
  long lVar3;
  long lVar4;
  uint uVar5;
  long lVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  long *plVar10;
  long local_14b8;
  long local_14b0;
  ulong local_14a8;
  long local_14a0;
  undefined4 local_1498;
  undefined1 local_1490;
  undefined2 local_1488 [8];
  long lStack_1478;
  uint auStack_1470 [4];
  long alStack_1460 [379];
  undefined4 local_884;
  int local_87c;
  undefined8 local_868;
  undefined8 local_860;
  undefined4 local_858;
  undefined8 local_850;
  undefined8 local_848;
  undefined8 local_840;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if ((*param_1 == '\0') && (param_5 != -1)) {
    local_848 = 0x10;
    local_850 = 0x800;
    local_840 = 0;
    local_860 = 0;
    local_858 = 0xffffffff;
    local_868 = 0;
    cVar1 = FUN_00308eb0(&local_868,param_5);
    if (cVar1 != '\0') {
      lVar3 = FUN_0100fd30(&local_868);
      lVar4 = FUN_003090d0(&local_868,*(undefined4 *)PTR_DAT_019b1be8,
                           *(undefined4 *)PTR_DAT_019b1be0);
      *(undefined4 *)(lVar3 + 0x40) = param_2;
      if (lVar4 != 0) {
        lVar8 = (long)*param_6;
        lVar9 = *(long *)(lVar4 + 0x10);
        FUN_00309360(&local_868,lVar4 + 0x10,*(undefined4 *)PTR_DAT_019b1bf0,lVar9 + lVar8);
        if (0 < lVar8) {
          param_6 = param_6 + 2;
          plVar10 = (long *)(lVar4 + 0x18);
          do {
            if (param_6[-1] != -0x7ee3623b) {
              lVar4 = *plVar10;
              *(int *)((long)plVar10 + lVar9 * 8 + lVar4 + 0x10) = param_6[-1];
              *(int *)((long)plVar10 + lVar9 * 8 + lVar4 + 0x14) = *param_6;
            }
            lVar9 = lVar9 + 1;
            param_6 = param_6 + 2;
            lVar8 = lVar8 + -1;
          } while (lVar8 != 0);
        }
      }
      uVar2 = FUN_0032e4f0(lVar3);
      *(undefined4 *)(param_1 + 4) = uVar2;
      lVar3 = 8;
      do {
        *(undefined2 *)((long)local_1488 + lVar3) = 0xffff;
        lVar3 = lVar3 + 0x30;
      } while (lVar3 != 0xc08);
      local_884 = 0;
      local_87c = -1;
      FUN_0030e200(local_1488,*(undefined4 *)(param_1 + 4),*(undefined4 *)PTR_DAT_0198e960,1);
      if (local_87c != -1) {
        do {
          local_1490 = 0;
          lVar8 = (long)local_87c;
          lVar3 = (&lStack_1478)[lVar8 * 6];
          lVar4 = *DAT_01a238a0;
          uVar5 = (int)*(uint *)(lVar3 + 0x20) >> 0xd;
          local_14a0 = (long)*(int *)(lVar3 + 4);
          lVar6 = (ulong)((uVar5 >> 0x12 | 0x3ff) & uVar5) * 0x40;
          lVar9 = *(long *)(lVar4 + 0x10 + lVar6);
          uVar7 = (ulong)((*(uint *)(lVar3 + 0x20) & 0x1fff) * *(int *)(lVar4 + 0x30 + lVar6));
          local_14b8 = (lVar9 + uVar7) -
                       ((long)*(int *)(lVar4 + 0x34 + lVar6) & *(ulong *)(lVar9 + 8 + uVar7));
          local_14b0 = alStack_1460[lVar8 * 6] + local_14a0;
          local_1498 = *(undefined4 *)(lVar3 + 0xc);
          local_14a8 = (ulong)auStack_1470[lVar8 * 0xc];
          FUN_00353610(&local_14b8,param_3,param_4);
          FUN_0030e7a0(local_1488);
        } while (local_87c != -1);
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

