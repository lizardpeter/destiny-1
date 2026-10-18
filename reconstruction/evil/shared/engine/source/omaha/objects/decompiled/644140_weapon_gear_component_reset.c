
void FUN_00644140(uint *param_1)

{
  long lVar1;
  long lVar2;
  ulong uVar3;
  uint uVar4;
  long lVar5;
  undefined8 local_50;
  undefined8 local_48;
  uint local_40;
  undefined8 local_38;
  undefined8 uStack_30;
  undefined8 local_28;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  param_1[0x22] = 0xffffffff;
  param_1[0x23] = 0xffffffff;
  param_1[0x20] = 0xffffffff;
  param_1[0x21] = 0xffffffff;
  param_1[0x1e] = 0xffffffff;
  param_1[0x1f] = 0xffffffff;
  param_1[0x1c] = 0xffffffff;
  param_1[0x1d] = 0xffffffff;
  param_1[0x1a] = 0xffffffff;
  param_1[0x1b] = 0xffffffff;
  param_1[0xc] = 0x811c9dc5;
  param_1[0xd] = 0;
  param_1[0xe] = 0x811c9dc5;
  param_1[0xf] = 0;
  param_1[0x10] = 0x811c9dc5;
  param_1[0x11] = 0;
  param_1[0x12] = 0x811c9dc5;
  param_1[0x13] = 0;
  param_1[0x14] = 0x811c9dc5;
  param_1[0x15] = 0;
  param_1[0x16] = 0x811c9dc5;
  param_1[0x17] = 0;
  param_1[0x18] = 0x811c9dc5;
  param_1[0x19] = 0;
  param_1[0x24] = 0;
  param_1[0x25] = 0xffffffff;
  param_1[0x26] = 0xffffffff;
  if (param_1[0xb] != 0xffffffff) {
    FUN_002d94f0(param_1[9]);
  }
  uVar4 = (int)*param_1 >> 0xd;
  lVar1 = *DAT_01a238a0;
  lVar5 = (ulong)((uVar4 >> 0x12 | 0x3ff) & uVar4) * 0x40;
  lVar2 = *(long *)(lVar1 + 0x10 + lVar5);
  uVar3 = (ulong)((*param_1 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar5));
  local_38 = 0;
  uStack_30 = 0;
  local_28 = 0;
  local_40 = param_1[4];
  local_50 = *(undefined8 *)param_1;
  local_48 = *(undefined8 *)(param_1 + 2);
  FUN_001d36a0(&local_50,*(undefined4 *)PTR_DAT_0191a898,
               *(long *)(param_1 + 2) + 0x70 +
               ((lVar2 + uVar3) -
               ((long)*(int *)(lVar1 + 0x34 + lVar5) & *(ulong *)(lVar2 + 8 + uVar3))),&local_38);
  FUN_0030c6a0(param_1,&local_38,*(undefined4 *)PTR_DAT_0191a8a0,3,1);
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

