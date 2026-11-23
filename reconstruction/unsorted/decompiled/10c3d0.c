
ulong FUN_0010c3d0(void)

{
  long *plVar1;
  char cVar2;
  ulong uVar3;
  uint local_30 [6];
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  cVar2 = FUN_001072c0(0x10,0,local_30);
  if (cVar2 == '\0') {
    uVar3 = 0xffffffff;
  }
  else {
    uVar3 = (ulong)local_30[0];
  }
  if (*plVar1 == local_18) {
    return uVar3;
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

