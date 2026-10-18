
void FUN_0029d9e0(long *param_1,undefined1 *param_2,undefined8 param_3)

{
  long *plVar1;
  undefined8 uVar2;
  undefined4 local_648 [2];
  undefined4 local_640;
  undefined1 local_63c;
  undefined1 local_638 [1536];
  long local_38;
  
  plVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  thunk_FUN_012aa986(local_638,0,0x600);
  local_640 = (undefined4)param_1[0xc96];
  local_63c = *param_2;
  thunk_FUN_012aa7c6(local_638,param_3,0x600);
  uVar2 = (**(code **)(*param_1 + 0x10))(param_1);
  local_648[0] = 0;
  FUN_00299d10(param_1,uVar2,0x1e,*(undefined4 *)PTR_DAT_0191a3f8,&local_640,0x608,local_648);
  if (*plVar1 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

