
ulong FUN_00bd5340(undefined8 param_1,short param_2)

{
  char cVar1;
  int iVar2;
  uint uVar3;
  ulong uVar4;
  undefined1 local_50 [40];
  undefined1 local_28;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  local_28 = 0;
  cVar1 = FUN_00bd51e0(param_1,local_50);
  uVar4 = 0xffffffff;
  if (cVar1 != '\0') {
    iVar2 = FUN_00353640(local_50,(int)param_2);
    if (iVar2 != -1) {
      uVar3 = FUN_006ed9f0(iVar2);
      uVar4 = (ulong)uVar3;
    }
  }
  if (*DAT_01a1f100 == local_20) {
    return uVar4;
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

