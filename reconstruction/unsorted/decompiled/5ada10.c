
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_005ada10(uint *param_1)

{
  int iVar1;
  long lVar2;
  long lVar3;
  undefined1 auVar4 [16];
  long *plVar5;
  char cVar6;
  int iVar7;
  uint uVar8;
  long lVar9;
  uint uVar10;
  long lVar11;
  ulong uVar12;
  ulong uVar13;
  long local_d0;
  long local_c8;
  undefined8 local_c0;
  undefined8 local_b8;
  uint local_b0;
  undefined1 local_a8;
  long local_a0;
  long local_98;
  undefined8 local_90;
  undefined8 local_88;
  uint local_80;
  undefined1 local_78;
  undefined8 local_70;
  undefined8 local_68;
  uint local_60;
  undefined8 local_58;
  undefined8 uStack_50;
  undefined8 local_48;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar10 = (int)*param_1 >> 0xd;
  lVar2 = *(long *)(param_1 + 2);
  lVar3 = *DAT_01a238a0;
  lVar9 = (ulong)((uVar10 >> 0x12 | 0x3ff) & uVar10) * 0x40;
  lVar11 = *(long *)(lVar3 + 0x10 + lVar9);
  iVar1 = *(int *)(lVar3 + 0x34 + lVar9);
  uVar13 = (ulong)((*param_1 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar9));
  uVar12 = *(ulong *)(lVar11 + 8 + uVar13);
  FUN_005adf60(param_1,1);
  FUN_005ae050(param_1,1);
  if (((param_1[0x272] != 0) && (param_1[0x272] != 0xffffffff)) && (param_1[0x274] != 0xffffffff)) {
    iVar7 = FUN_00352ee0(param_1 + 0x272);
    if (iVar7 != -1) {
      FUN_006286a0(param_1 + 0x94,iVar7);
    }
  }
  local_58 = 0;
  uStack_50 = 0;
  local_48 = 0;
  local_70 = *(undefined8 *)param_1;
  local_68 = *(undefined8 *)(param_1 + 2);
  local_60 = param_1[4];
  FUN_001d36a0(&local_70,*(undefined4 *)PTR_DAT_0191a888,
               lVar2 + 0x388 + ((lVar11 + uVar13) - ((long)iVar1 & uVar12)),&local_58);
  FUN_0030c6a0(param_1,&local_58,*(undefined4 *)PTR_DAT_0191a890,0,1);
  uVar10 = param_1[0x2c4];
  if (uVar10 != 0xffffffff) {
    auVar4 = vandps_avx(ZEXT416(param_1[0x6d]),_DAT_01641920);
    if (DAT_016418cc <= auVar4._0_4_) {
      auVar4 = vandps_avx(ZEXT416((uint)((float)param_1[0x6e] + DAT_016418d0)),_DAT_01641920);
      if (DAT_016418cc <= auVar4._0_4_) {
        local_78 = 0;
        uVar8 = (int)param_1[0x2c2] >> 0xd;
        lVar2 = *DAT_01a238a0;
        lVar11 = (ulong)(((uint)((int)uVar10 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar10 >> 0xd) * 0x40;
        lVar9 = (ulong)((uVar8 >> 0x12 | 0x3ff) & uVar8) * 0x40;
        lVar3 = *(long *)(lVar2 + 0x10 + lVar9);
        uVar12 = (ulong)((param_1[0x2c2] & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar9));
        local_a0 = (lVar3 + uVar12) -
                   ((long)*(int *)(lVar2 + 0x34 + lVar9) & *(ulong *)(lVar3 + 8 + uVar12));
        lVar3 = *(long *)(lVar2 + 0x10 + lVar11);
        uVar12 = (ulong)((uVar10 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar11));
        local_98 = ((lVar3 + uVar12) -
                   ((long)*(int *)(lVar2 + 0x34 + lVar11) & *(ulong *)(lVar3 + 8 + uVar12))) +
                   *(long *)(param_1 + 0x2c6);
        local_80 = param_1[0x2c8];
        local_90 = *(undefined8 *)(param_1 + 0x2c4);
        local_88 = *(undefined8 *)(param_1 + 0x2c6);
        FUN_003543d0(&local_a0,param_1 + 0x2cc);
        uVar10 = FUN_00591c80(param_1[0x6d]);
        param_1[0x2ca] = uVar10;
      }
    }
  }
  uVar10 = param_1[0x2ac];
  if (uVar10 != 0xffffffff) {
    local_a8 = 0;
    uVar8 = (int)param_1[0x2aa] >> 0xd;
    lVar2 = *DAT_01a238a0;
    lVar11 = (ulong)(((uint)((int)uVar10 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar10 >> 0xd) * 0x40;
    lVar9 = (ulong)((uVar8 >> 0x12 | 0x3ff) & uVar8) * 0x40;
    lVar3 = *(long *)(lVar2 + 0x10 + lVar9);
    uVar12 = (ulong)((param_1[0x2aa] & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar9));
    local_d0 = (lVar3 + uVar12) -
               ((long)*(int *)(lVar2 + 0x34 + lVar9) & *(ulong *)(lVar3 + 8 + uVar12));
    lVar3 = *(long *)(lVar2 + 0x10 + lVar11);
    uVar12 = (ulong)((uVar10 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar11));
    local_c8 = ((lVar3 + uVar12) -
               ((long)*(int *)(lVar2 + 0x34 + lVar11) & *(ulong *)(lVar3 + 8 + uVar12))) +
               *(long *)(param_1 + 0x2ae);
    local_b0 = param_1[0x2b0];
    local_c0 = *(undefined8 *)(param_1 + 0x2ac);
    local_b8 = *(undefined8 *)(param_1 + 0x2ae);
    FUN_00353890(param_1[0x6c],&local_d0,1);
  }
  if (((param_1[0x1d2] != 0) && (param_1[0x1d2] != 0xffffffff)) && (param_1[0x1d4] != 0xffffffff)) {
    cVar6 = FUN_00352ee0(param_1 + 0x1d2);
    uVar10 = 0;
    if (cVar6 == '\0') goto LAB_005addac;
  }
  uVar10 = param_1[0x85];
LAB_005addac:
  FUN_005ae100(uVar10,param_1);
  param_1[0x87] = param_1[0x7e];
  param_1[0x88] = param_1[0x7f];
  plVar5 = DAT_01a1f100;
  param_1[0x89] = param_1[0x2fa];
  if (*plVar5 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

