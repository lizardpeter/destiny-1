
void FUN_00353340(long param_1,undefined4 *param_2)

{
  long lVar1;
  long lVar2;
  long *plVar3;
  ulong uVar4;
  uint uVar5;
  long lVar6;
  long *plVar7;
  undefined4 local_50 [2];
  undefined8 local_48;
  undefined1 local_40 [8];
  code *local_38;
  long local_30;
  long local_28;
  
  plVar3 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  FUN_001cfca0(local_40,param_1);
  uVar5 = (int)*(uint *)(param_1 + 8) >> 0xd;
  lVar6 = (ulong)((uVar5 >> 0x12 | 0x3ff) & uVar5) * 0x40;
  lVar1 = *DAT_01a238a0;
  lVar2 = *(long *)(lVar1 + 0x10 + lVar6);
  uVar4 = (ulong)((*(uint *)(param_1 + 8) & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar6));
  plVar7 = (long *)(((lVar2 + uVar4) -
                    ((long)*(int *)(lVar1 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar4))) +
                   *(long *)(param_1 + 0x10) + local_30);
  if (((ulong)local_38 & 1) != 0) {
    local_38 = *(code **)(local_38 + *plVar7 + -1);
  }
  local_50[0] = *param_2;
  local_48 = *(undefined8 *)(param_2 + 2);
  (*local_38)(plVar7,local_50);
  if (*plVar3 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

