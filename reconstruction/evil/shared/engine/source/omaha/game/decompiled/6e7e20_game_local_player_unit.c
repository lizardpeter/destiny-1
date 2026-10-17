
ulong FUN_006e7e20(void)

{
  int iVar1;
  ulong uVar2;
  
  iVar1 = FUN_00923790();
  if (iVar1 == -1) {
    return 0xffffffff;
  }
  iVar1 = FUN_009236b0(iVar1);
  uVar2 = (ulong)(ushort)iVar1;
  if (iVar1 == -1) {
    uVar2 = 0xffffffff;
  }
  return uVar2;
}

