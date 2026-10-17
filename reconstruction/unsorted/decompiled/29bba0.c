
void FUN_0029bba0(long *param_1)

{
  char cVar1;
  undefined8 uVar2;
  undefined4 local_28 [2];
  undefined4 local_20 [2];
  long local_18;
  
  local_18 = *DAT_01a1f100;
  local_28[0] = 0;
  cVar1 = (**(code **)(*param_1 + 0x18))();
  if (cVar1 != '\0') {
    uVar2 = (**(code **)(*param_1 + 0x10))(param_1);
    local_20[0] = 0;
    FUN_00299d10(param_1,uVar2,0x30,*(undefined4 *)PTR_DAT_0191a478,local_28,4,local_20);
  }
  if (*DAT_01a1f100 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

