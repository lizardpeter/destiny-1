
ulong FUN_00f81f80(undefined8 *param_1,uint param_2,uint param_3,uint param_4,uint param_5,
                  undefined4 param_6,uint param_7,uint param_8,ulong *param_9,ulong *param_10)

{
  char cVar1;
  uint uVar2;
  int iVar3;
  undefined4 uVar4;
  ulong uVar5;
  uint uVar6;
  uint uVar7;
  uint uVar8;
  ulong uVar9;
  ulong local_108;
  uint local_100;
  int local_fc;
  int local_f8;
  uint local_f4;
  ulong local_f0;
  int local_e4;
  ulong local_e0 [6];
  ulong local_b0;
  undefined4 local_a0;
  uint uStack_9c;
  uint uStack_98;
  uint uStack_94;
  undefined4 uStack_90;
  int iStack_8c;
  undefined8 uStack_88;
  undefined4 local_80;
  undefined4 local_7c;
  uint local_68 [2];
  long local_60;
  ulong uVar10;
  
  local_60 = *DAT_01a1f100;
  uVar10 = 0;
  uVar9 = 0;
  *(undefined4 *)(param_1 + 5) = 0;
  param_1[4] = 0;
  param_1[3] = 0;
  param_1[2] = 0;
  param_1[1] = 0;
  *param_1 = 0;
  local_68[0] = param_5;
  if (param_7 < param_8) {
    uVar5 = 0;
    uVar9 = uVar10;
    goto LAB_00f823df;
  }
  if (0x16 < (param_5 & 0xff)) {
    uVar5 = 0;
    uVar9 = uVar10;
    goto LAB_00f823df;
  }
  if ((param_5 & 0xff) == 0) {
    uVar5 = 0;
    uVar9 = uVar10;
    goto LAB_00f823df;
  }
  uVar5 = 0;
  if ((param_5 & 0xff | 2) == 0xf) goto LAB_00f823df;
  uVar9 = 0;
  cVar1 = FUN_00f7d980(local_68,0);
  uVar5 = 0;
  if (cVar1 == '\0') goto LAB_00f823df;
  cVar1 = FUN_00f7d780(local_68,0);
  if (cVar1 != '\0') {
    uVar6 = param_2;
    uVar2 = param_3;
    if (param_9 != (ulong *)0x0) {
      uVar2 = param_3 + 7 & 0xfffffff8;
      uVar6 = param_2 + 7 & 0xfffffff8;
    }
    local_80 = 0;
    _uStack_98 = CONCAT44(uVar2,uVar6);
    uStack_88 = 0;
    _uStack_90 = CONCAT44(1 << ((byte)param_8 & 0x1f),1);
    local_7c = 0;
    _local_a0 = CONCAT44(local_68[0],param_6);
    local_e0[0] = 0;
    local_e0[1] = 0;
    local_e0[2] = 0;
    local_e0[3] = 0;
    local_b0 = 0;
    local_e0[5] = 0;
    local_e0[4] = 0;
    iVar3 = FUN_00f85cb0(local_e0,&local_a0);
    uVar9 = local_b0;
    if (iVar3 == 0) {
      uVar6 = (uint)local_b0;
      *(uint *)((long)param_1 + 0xc) =
           param_4 * 0x2000 + 0xffe000 & 0xffe000 | *(uint *)((long)param_1 + 0xc) & 0xff001800;
      FUN_00f82430(param_1,local_68[0]);
      uVar8 = uVar6 & 0x1f;
      uVar7 = *(uint *)(param_1 + 2) | 0x20000;
      *(uint *)(param_1 + 2) = uVar7;
      uVar2 = ((uint)(local_e0[0] >> 3) & 0x1fffffff) - 1;
      *(uint *)((long)param_1 + 4) =
           (uVar2 & 0x7ff) << 0x14 | uVar2 & 0x7ff | *(uint *)((long)param_1 + 4) & 0x800ff800;
      *(uint *)(param_1 + 1) =
           ((uint)((int)(local_e0[0] >> 0x20) * (int)local_e0[0]) >> 6) + 0x3fffff & 0x3fffff |
           *(uint *)(param_1 + 1) & 0xffc00000;
      *(uint *)(param_1 + 3) = param_2 & 0xffff | param_3 << 0x10;
      *(uint *)((long)param_1 + 0x14) =
           *(uint *)((long)param_1 + 0x14) & 0xfffe0c00 |
           (param_8 & 3) << 0xf | (param_7 & 7) << 0xc | uVar8 << 5 | uVar8;
      if (param_9 == (ulong *)0x0) {
LAB_00f822f7:
        uVar9 = local_e0[0];
        if ((param_10 != (ulong *)0x0) && (0 < (int)param_7)) {
          if (param_9 == (ulong *)0x0) goto LAB_00f823da;
          *(uint *)(param_1 + 2) = uVar7 | 0x4000;
          uVar4 = FUN_00f7d5f0(param_7,param_8);
          iVar3 = FUN_00f86e40(&local_108,&local_100,&local_f8,&local_fc,uVar9 & 0xffffffff,
                               uVar9 >> 0x20,param_4,uVar6,uVar4);
          uVar9 = 0;
          uVar5 = 0;
          if (iVar3 != 0) goto LAB_00f823df;
          *param_10 = (ulong)local_100 << 0x20 | local_108 & 0xffffffff;
          *(uint *)(param_1 + 5) =
               ((uint)(local_fc * local_f8) >> 6) + 0x3fffff & 0x3fffff |
               *(uint *)(param_1 + 5) & 0xffc00000;
        }
        uVar5 = 0;
        if (param_4 * local_e0[2] >> 0x20 == 0) {
          uVar5 = param_4 * local_e0[2] & 0xffffffff;
        }
        uVar9 = local_e0[3] & 0xffffffff00000000;
        goto LAB_00f823df;
      }
      FUN_00f87240(&local_e4,uVar9 & 0xffffffff);
      if (local_e4 != 4) {
        iVar3 = FUN_00f7d710(local_68);
        if (iVar3 != 0x80) {
          uVar9 = 0;
          iVar3 = FUN_00f86d10(&local_f0,&local_f4,0,0,local_e0[0],local_e0[0] >> 0x20,param_4,0);
          uVar5 = 0;
          if (iVar3 != 0) goto LAB_00f823df;
          *param_9 = (ulong)local_f4 << 0x20 | local_f0 & 0xffffffff;
          *(uint *)(param_1 + 4) =
               *(uint *)(param_1 + 4) & 0xffffc000 |
               ((uint)(local_f0 / param_4) >> 7) + 0x3fff & 0x3fff;
          uVar7 = *(uint *)(param_1 + 2) & 0xfff7dfff | 0x2000;
          *(uint *)(param_1 + 2) = uVar7;
          goto LAB_00f822f7;
        }
      }
    }
  }
LAB_00f823da:
  uVar9 = 0;
  uVar5 = 0;
LAB_00f823df:
  if (*DAT_01a1f100 == local_60) {
    return uVar5 | uVar9;
  }
  uVar9 = thunk_FUN_012aa7f6();
  return uVar9;
}

