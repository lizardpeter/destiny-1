
void FUN_00642be0(uint *param_1,undefined4 *param_2)

{
  long lVar1;
  long lVar2;
  long *plVar3;
  undefined8 uVar4;
  ulong uVar5;
  long lVar6;
  uint uVar7;
  undefined8 local_60;
  undefined8 local_58;
  uint local_50;
  undefined8 local_48;
  undefined8 uStack_40;
  undefined8 local_38;
  long local_30;
  
  plVar3 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  uStack_40 = *(undefined8 *)(param_2 + 2);
  local_48 = CONCAT44(local_48._4_4_,*param_2);
  uVar4 = FUN_00078970(&local_48,*(undefined4 *)PTR_DAT_019b1bb0);
  thunk_FUN_012aa7c6(param_1,uVar4,0x160);
  uVar7 = (int)*param_1 >> 0xd;
  lVar6 = (ulong)((uVar7 >> 0x12 | 0x3ff) & uVar7) * 0x40;
  lVar1 = *DAT_01a238a0;
  lVar2 = *(long *)(lVar1 + 0x10 + lVar6);
  uVar5 = (ulong)((*param_1 & 0x1fff) * *(int *)(lVar1 + 0x30 + lVar6));
  local_48 = 0;
  uStack_40 = 0;
  local_38 = 0;
  local_50 = param_1[4];
  local_60 = *(undefined8 *)param_1;
  local_58 = *(undefined8 *)(param_1 + 2);
  FUN_001d36a0(&local_60,*(undefined4 *)PTR_DAT_0191a898,
               *(long *)(param_1 + 2) + 0x70 +
               ((lVar2 + uVar5) -
               ((long)*(int *)(lVar1 + 0x34 + lVar6) & *(ulong *)(lVar2 + 8 + uVar5))),&local_48);
  FUN_0030c6a0(param_1,&local_48,*(undefined4 *)PTR_DAT_0191a8a0,3,1);
  if (*plVar3 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

