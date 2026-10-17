
void FUN_007a5250(long param_1)

{
  char cVar1;
  undefined4 uVar2;
  
  uVar2 = FUN_00785060(0);
  if ((*(byte *)(param_1 + 0x6b8) & 1) != 0) {
    FUN_007a5d80(param_1);
    return;
  }
  if ((((*(byte *)(param_1 + 0x6b8) & 4) != 0) && (cVar1 = FUN_007724f0(1), cVar1 != '\0')) &&
     (cVar1 = FUN_007851a0(1,uVar2), cVar1 == '\0')) {
    return;
  }
  if ((((*(byte *)(param_1 + 0x6b8) & 2) != 0) && (cVar1 = FUN_007724f0(0), cVar1 != '\0')) &&
     (cVar1 = FUN_007851a0(0,uVar2), cVar1 == '\0')) {
    return;
  }
  *(undefined1 *)(param_1 + 0x6b8) = 0;
  return;
}

