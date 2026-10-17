
undefined8 FUN_00bd5bf0(undefined8 param_1)

{
  char cVar1;
  undefined8 uVar2;
  undefined1 local_40 [40];
  undefined1 local_18;
  long local_10;
  
  local_10 = *DAT_01a1f100;
  local_18 = 0;
  cVar1 = FUN_00bd51e0(param_1,local_40);
  uVar2 = 0xffffffff;
  if (cVar1 != '\0') {
    uVar2 = FUN_00354300(local_40);
  }
  if (*DAT_01a1f100 == local_10) {
    return uVar2;
  }
  uVar2 = thunk_FUN_012aa7f6();
  return uVar2;
}

