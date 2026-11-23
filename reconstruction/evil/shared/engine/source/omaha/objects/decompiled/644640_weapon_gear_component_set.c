
void FUN_00644640(uint *param_1,uint *param_2)

{
  undefined8 uVar1;
  undefined8 uVar2;
  long lVar3;
  long lVar4;
  ulong uVar5;
  uint uVar6;
  long lVar7;
  undefined8 local_50;
  undefined8 local_48;
  uint local_40;
  undefined8 local_38;
  undefined8 uStack_30;
  undefined8 local_28;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  param_1[0xc] = *param_2;
  param_1[0xd] = param_2[1];
  param_1[0xe] = param_2[2];
  param_1[0xf] = param_2[3];
  param_1[0x10] = param_2[4];
  param_1[0x11] = param_2[5];
  param_1[0x12] = param_2[6];
  param_1[0x13] = param_2[7];
  param_1[0x14] = param_2[8];
  param_1[0x15] = param_2[9];
  param_1[0x16] = param_2[10];
  param_1[0x17] = param_2[0xb];
  param_1[0x18] = param_2[0xc];
  param_1[0x19] = param_2[0xd];
  uVar1 = *(undefined8 *)(param_2 + 0x16);
  uVar2 = *(undefined8 *)(param_2 + 0x18);
  param_1[0x26] = param_2[0x1a];
  *(undefined8 *)(param_1 + 0x24) = uVar2;
  *(undefined8 *)(param_1 + 0x22) = uVar1;
  *(undefined8 *)(param_1 + 0x20) = *(undefined8 *)(param_2 + 0x14);
  *(undefined8 *)(param_1 + 0x1e) = *(undefined8 *)(param_2 + 0x12);
  uVar1 = *(undefined8 *)(param_2 + 0xe);
  *(undefined8 *)(param_1 + 0x1c) = *(undefined8 *)(param_2 + 0x10);
  *(undefined8 *)(param_1 + 0x1a) = uVar1;
  if (param_1[0xb] != 0xffffffff) {
    FUN_002d94f0(param_1[9]);
  }
  uVar6 = (int)*param_1 >> 0xd;
  lVar3 = *DAT_01a238a0;
  lVar7 = (ulong)((uVar6 >> 0x12 | 0x3ff) & uVar6) * 0x40;
  lVar4 = *(long *)(lVar3 + 0x10 + lVar7);
  uVar5 = (ulong)((*param_1 & 0x1fff) * *(int *)(lVar3 + 0x30 + lVar7));
  local_38 = 0;
  uStack_30 = 0;
  local_28 = 0;
  local_40 = param_1[4];
  local_50 = *(undefined8 *)param_1;
  local_48 = *(undefined8 *)(param_1 + 2);
  FUN_001d36a0(&local_50,*(undefined4 *)PTR_DAT_0191a898,
               *(long *)(param_1 + 2) + 0x70 +
               ((lVar4 + uVar5) -
               ((long)*(int *)(lVar3 + 0x34 + lVar7) & *(ulong *)(lVar4 + 8 + uVar5))),&local_38);
  FUN_0030c6a0(param_1,&local_38,*(undefined4 *)PTR_DAT_0191a8a0,3,1);
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

