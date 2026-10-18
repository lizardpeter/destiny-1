
void FUN_00923590(ulong param_1)

{
  int iVar1;
  byte bVar2;
  int iVar3;
  long lVar4;
  ulong uVar5;
  
  if ((*(char *)(DAT_0273eb80 + 200 + (param_1 & 0xffff)) != '\0') && ((int)param_1 != -1)) {
    iVar3 = -1;
    while (((bVar2 = *(byte *)(DAT_0273eb80 + 200 + (param_1 & 0xffff)), bVar2 != 0 && (iVar3 == -1)
            ) && ((bVar2 & 1) != 0))) {
      bVar2 = (bVar2 & 1) - 1;
      iVar3 = (int)(char)bVar2;
      lVar4 = (long)iVar3;
      iVar1 = *(int *)(DAT_0273eb80 + 0xc0 + lVar4 * 4);
      if (iVar1 != -1) {
        uVar5 = (ulong)(ushort)iVar1;
        if (*(int *)(DAT_0273eb80 + 0xc4 + lVar4 * 4) != -1) {
          FUN_0091b490(iVar3,0xffffffff);
          FUN_0090a340(iVar3,0xffffffff,0);
          *(undefined4 *)(DAT_0273eb80 + 0xc4 + lVar4 * 4) = 0xffffffff;
        }
        *(byte *)(DAT_0273eb80 + 200 + uVar5) =
             ~(byte)(1 << (bVar2 & 0x1f)) & *(byte *)(DAT_0273eb80 + 200 + uVar5);
        *(undefined4 *)(DAT_0273eb80 + 0xc0 + lVar4 * 4) = 0xffffffff;
        *(short *)(DAT_0273eb80 + 0xbc) = *(short *)(DAT_0273eb80 + 0xbc) + -1;
      }
    }
  }
  return;
}

