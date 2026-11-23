
void FUN_00571150(long param_1,undefined4 param_2,long param_3,undefined8 param_4)

{
  long *plVar1;
  char cVar2;
  int iVar3;
  long local_a8;
  undefined8 local_a0;
  undefined8 local_98;
  undefined8 local_90;
  long local_88;
  undefined8 local_80;
  undefined8 local_78;
  int local_70;
  undefined8 local_68;
  undefined8 local_60;
  ulong local_58;
  undefined8 local_50;
  ulong local_48;
  undefined8 local_40;
  long local_38;
  
  plVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  cVar2 = FUN_005428c0();
  if (cVar2 != '\0') {
    local_48 = local_48 & 0xffffffff00000000;
    local_40 = 0;
    iVar3 = FUN_00551bd0(param_2);
    if (iVar3 != -1) {
      FUN_001d3320(&local_58,iVar3,*(undefined8 *)(param_3 + 8));
      local_40 = local_50;
      local_48 = local_58;
    }
    local_68 = (ulong)local_68._4_4_ << 0x20;
    local_60 = 0;
    if (0 < *(int *)(param_3 + 0x18)) {
      local_78 = *(undefined8 *)(param_3 + 0x10);
      local_70 = *(int *)(param_3 + 0x18);
      FUN_001d3320(&local_88,*(undefined4 *)PTR_DAT_019e4c20,&local_78);
      local_60 = local_80;
      local_68 = local_88;
    }
    local_98 = (ulong)local_98._4_4_ << 0x20;
    local_90 = 0;
    iVar3 = FUN_00551c10(param_2);
    if (iVar3 != -1) {
      FUN_001d3320(&local_a8,iVar3,param_4);
      local_90 = local_a0;
      local_98 = local_a8;
    }
    cVar2 = FUN_00001f70(0);
    if (cVar2 != '\0') {
      FUN_00bf5110(param_1 + 0x58,&local_48,&local_68,&local_98);
    }
    FUN_0023a4a0();
  }
  if (*plVar1 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

