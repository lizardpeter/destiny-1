
void FUN_0029b310(long *param_1,undefined8 param_2)

{
  char cVar1;
  undefined8 uVar2;
  undefined4 local_240 [2];
  undefined1 local_238 [528];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  cVar1 = (**(code **)(*param_1 + 0x18))();
  if (cVar1 != '\0') {
    thunk_FUN_012aa7c6(local_238,param_2,0x210);
    uVar2 = (**(code **)(*param_1 + 0x10))(param_1);
    local_240[0] = 0;
    FUN_00299d10(param_1,uVar2,0x21,*(undefined4 *)PTR_DAT_0191a448,local_238,0x210,local_240);
  }
  if (*DAT_01a1f100 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

