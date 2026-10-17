
bool FUN_0006d4d0(long param_1,undefined8 param_2,undefined4 param_3,undefined8 param_4)

{
  undefined1 uVar1;
  int iVar2;
  undefined8 local_280;
  undefined1 local_278 [32];
  undefined1 local_258 [560];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  local_280 = 0x20;
  iVar2 = FUN_00f6a940(local_258,*(undefined4 *)(param_1 + 4),param_1 + 8,
                       *(ulong *)(param_1 + 0x28) & 0xffffffff);
  if (((iVar2 == 0) && (iVar2 = FUN_00f6ab60(local_258,param_2,param_3), iVar2 == 0)) &&
     (iVar2 = FUN_00f6a730(local_258,local_278,&local_280), iVar2 == 0)) {
    iVar2 = thunk_FUN_012aa826(param_4,local_278,0x20);
    if (*DAT_01a1f100 == local_28) {
      return iVar2 == 0;
    }
  }
  else if (*DAT_01a1f100 == local_28) {
    return false;
  }
  uVar1 = thunk_FUN_012aa7f6();
  return (bool)uVar1;
}

