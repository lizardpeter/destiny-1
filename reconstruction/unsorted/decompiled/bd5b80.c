
void FUN_00bd5b80(undefined8 param_1,undefined8 *param_2)

{
  char cVar1;
  undefined4 uVar2;
  undefined1 local_50 [40];
  undefined1 local_28;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  local_28 = 0;
  cVar1 = FUN_00bd51e0(param_1,local_50);
  if (cVar1 == '\0') {
    *param_2 = 0xffffffffffffffff;
  }
  else {
    uVar2 = FUN_00354300(local_50);
    *(undefined4 *)param_2 = uVar2;
    uVar2 = FUN_00354cf0(local_50);
    *(undefined4 *)((long)param_2 + 4) = uVar2;
  }
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

