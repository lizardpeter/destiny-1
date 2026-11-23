
void FUN_00644810(uint *param_1,char param_2)

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
  if (param_2 != (char)param_1[0x67]) {
    *(char *)(param_1 + 0x67) = param_2;
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
  }
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

