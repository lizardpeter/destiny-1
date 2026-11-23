
ulong FUN_00923200(int param_1)

{
  int iVar1;
  ulong in_RAX;
  ulong uVar2;
  
  uVar2 = in_RAX & 0xffffffffffffff00;
  if (param_1 != -1) {
    iVar1 = *(int *)(DAT_0273eb80 + 4 + (long)param_1 * 4);
    uVar2 = (ulong)CONCAT31((int3)((uint)iVar1 >> 8),iVar1 != -1);
  }
  return uVar2;
}

