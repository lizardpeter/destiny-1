
undefined8 FUN_0029bc40(long *param_1,undefined4 param_2)

{
  char extraout_AL;
  char cVar1;
  undefined8 uVar2;
  undefined7 extraout_var;
  undefined7 uVar3;
  undefined4 local_30 [2];
  undefined4 local_28 [2];
  long local_20;
  
  local_20 = *DAT_01a1f100;
  uVar2 = (**(code **)(*param_1 + 0x18))();
  if ((char)uVar2 == '\0') {
    cVar1 = *(char *)((long)param_1 + 0x64a9);
    uVar3 = (undefined7)((ulong)uVar2 >> 8);
  }
  else {
    local_30[0] = param_2;
    uVar2 = (**(code **)(*param_1 + 0x10))(param_1);
    local_28[0] = 0;
    FUN_00299d10(param_1,uVar2,0x13,*(undefined4 *)PTR_DAT_0191a398,local_30,4,local_28);
    *(char *)((long)param_1 + 0x64a9) = extraout_AL;
    cVar1 = extraout_AL;
    uVar3 = extraout_var;
  }
  if (*DAT_01a1f100 == local_20) {
    return CONCAT71(uVar3,cVar1 != '\0');
  }
  uVar2 = thunk_FUN_012aa7f6();
  return uVar2;
}

