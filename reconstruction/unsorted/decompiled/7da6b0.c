
ulong FUN_007da6b0(long param_1,int param_2)

{
  uint3 uVar1;
  int iVar2;
  ulong uVar3;
  bool bVar4;
  
  iVar2 = DAT_02709868;
  bVar4 = *(int *)(param_1 + 0x2c) != DAT_02709868;
  if (bVar4) {
    *(int *)(param_1 + 0x2c) = DAT_02709868;
  }
  if ((*(char *)(param_1 + 0x11) == '\0') && (*(int *)(param_1 + 0xc) != param_2)) {
    *(int *)(param_1 + 0xc) = param_2;
    *(undefined1 *)(param_1 + 0x10) = 1;
  }
  uVar1 = (uint3)((uint)iVar2 >> 8);
  uVar3 = CONCAT71((uint7)uVar1,1);
  if (!bVar4) {
    uVar3 = (ulong)CONCAT31(uVar1,*(char *)(param_1 + 0x10) != '\0');
  }
  *(undefined1 *)(param_1 + 0x10) = 0;
  return uVar3;
}

