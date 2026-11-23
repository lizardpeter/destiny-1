
undefined8 FUN_0029de50(long *param_1,undefined8 param_2,undefined4 param_3)

{
  char cVar1;
  int iVar2;
  undefined8 uVar3;
  undefined1 local_405c [4];
  undefined1 local_4058 [20];
  undefined4 local_4044;
  undefined1 local_3f88;
  undefined1 local_3f80 [16200];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_001d93e0(local_3f80);
  uVar3 = FUN_001d9450(local_3f80,local_405c);
  local_4044 = 1;
  FUN_00072240(local_4058,param_2,param_3);
  local_3f88 = 0;
  FUN_00072400(local_4058);
  cVar1 = FUN_002c9a90(*(undefined4 *)PTR_DAT_0191a1c8,local_4058,local_3f80,local_3f80,1);
  iVar2 = FUN_00072c70(local_4058,0x20);
  if ((iVar2 < 0) || (8000 < iVar2)) {
    FUN_00072650(local_4058);
  }
  else {
    FUN_000730b0(local_4058,uVar3,iVar2 << 3);
    FUN_00072650(local_4058);
    if (cVar1 != '\0') {
      (**(code **)(*param_1 + 0x10))(param_1);
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

