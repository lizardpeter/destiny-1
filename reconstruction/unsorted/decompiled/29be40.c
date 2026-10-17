
void FUN_0029be40(long *param_1,char *param_2,undefined8 param_3,undefined1 param_4)

{
  char cVar1;
  undefined8 uVar2;
  undefined4 local_648 [2];
  char local_640 [4];
  undefined1 local_63c [1536];
  undefined1 local_3c;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  thunk_FUN_012aa986(local_63c,0,0x600);
  cVar1 = *param_2;
  local_640[0] = cVar1;
  thunk_FUN_012aa7c6(local_63c,param_3,0x600);
  local_3c = param_4;
  if (cVar1 != '@') {
    FUN_000a0760(param_1 + 0xd00);
  }
  uVar2 = (**(code **)(*param_1 + 0x10))(param_1);
  local_648[0] = 0;
  FUN_00299d10(param_1,uVar2,0x19,*(undefined4 *)PTR_DAT_0191a3b0,local_640,0x608,local_648);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

