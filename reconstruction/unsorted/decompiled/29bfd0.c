
void FUN_0029bfd0(long *param_1,byte *param_2,long param_3)

{
  byte bVar1;
  uint uVar2;
  undefined8 uVar3;
  undefined4 local_640 [2];
  byte local_638 [4];
  undefined1 local_634 [1540];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  thunk_FUN_012aa986(local_634,0,0x600);
  bVar1 = *param_2;
  local_638[0] = bVar1;
  if (param_3 == 0) {
    thunk_FUN_012aa986(local_634,0,0x600);
  }
  else {
    thunk_FUN_012aa7c6(local_634,param_3,0x600);
  }
  uVar2 = FUN_0012d700(param_1 + 0xd00);
  if (bVar1 == uVar2) {
    FUN_000a0760(param_1 + 0xd00);
  }
  uVar3 = (**(code **)(*param_1 + 0x10))(param_1);
  local_640[0] = 0;
  FUN_00299d10(param_1,uVar3,0x20,*(undefined4 *)PTR_DAT_0191a430,local_638,0x604,local_640);
  if (*DAT_01a1f100 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

