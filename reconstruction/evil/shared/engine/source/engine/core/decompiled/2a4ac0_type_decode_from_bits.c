
ulong FUN_002a4ac0(undefined4 param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  long *plVar1;
  byte bVar2;
  ulong uVar3;
  undefined1 local_108 [16];
  int local_f8;
  undefined4 local_f4;
  int local_e4;
  undefined1 local_38;
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  local_f4 = 1;
  FUN_00072240(local_108);
  local_38 = 0;
  FUN_00072400(local_108);
  bVar2 = FUN_002c9a90(param_1,local_108,param_4,param_4,1);
  FUN_00072650(local_108);
  if (*plVar1 == local_30) {
    return (ulong)CONCAT31((int3)((uint)(local_f8 * 8) >> 8),bVar2 & local_e4 <= local_f8 * 8);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

