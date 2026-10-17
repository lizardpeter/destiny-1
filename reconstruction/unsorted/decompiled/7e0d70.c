
void FUN_007e0d70(long *param_1,undefined8 param_2)

{
  long *plVar1;
  int iVar2;
  undefined1 local_30 [16];
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  FUN_007da6f0(param_2);
  iVar2 = thunk_FUN_012aba76(local_30,0x10);
  if (iVar2 == 0) {
    thunk_FUN_012aba86(*(undefined4 *)(*param_1 + 0x80),local_30,0x10);
  }
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

