
void FUN_0029bf30(long *param_1,undefined1 param_2,undefined8 param_3)

{
  long *plVar1;
  undefined8 uVar2;
  undefined4 local_630 [2];
  undefined1 local_628 [4];
  undefined1 local_624 [1540];
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  local_628[0] = param_2;
  thunk_FUN_012aa7c6(local_624,param_3,0x600);
  uVar2 = (**(code **)(*param_1 + 0x10))(param_1);
  local_630[0] = 0;
  FUN_00299d10(param_1,uVar2,0x1a,*(undefined4 *)PTR_DAT_0191a3d0,local_628,0x604,local_630);
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

