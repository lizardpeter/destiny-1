
void FUN_00923430(int param_1,uint param_2)

{
  uint uVar1;
  long lVar2;
  ulong uVar3;
  long lVar4;
  
  lVar4 = (long)param_1;
  uVar1 = *(uint *)(DAT_0273eb80 + 0xc0 + lVar4 * 4);
  if (uVar1 != param_2) {
    if (param_2 == 0xffffffff) {
      uVar3 = (ulong)(ushort)uVar1;
      if (*(int *)(DAT_0273eb80 + 0xc4 + lVar4 * 4) != -1) {
        FUN_0091b490(param_1,0xffffffff);
        FUN_0090a340(param_1,0xffffffff,0);
        *(undefined4 *)(DAT_0273eb80 + 0xc4 + lVar4 * 4) = 0xffffffff;
      }
      *(byte *)(DAT_0273eb80 + 200 + uVar3) =
           ~(byte)(1 << ((byte)param_1 & 0x1f)) & *(byte *)(DAT_0273eb80 + 200 + uVar3);
      *(undefined4 *)(DAT_0273eb80 + 0xc0 + lVar4 * 4) = 0xffffffff;
      *(short *)(DAT_0273eb80 + 0xbc) = *(short *)(DAT_0273eb80 + 0xbc) + -1;
    }
    else {
      lVar2 = *(long *)(DAT_0273ea80 + 8);
      FUN_00923430(param_1,0xffffffff);
      *(uint *)(DAT_0273eb80 + 0xc0 + lVar4 * 4) = param_2;
      uVar3 = (ulong)param_2 & 0xffff;
      *(byte *)(DAT_0273eb80 + 200 + uVar3) =
           *(byte *)(DAT_0273eb80 + 200 + uVar3) | (byte)(1 << ((byte)param_1 & 0x1f));
      *(short *)(DAT_0273eb80 + 0xbc) = *(short *)(DAT_0273eb80 + 0xbc) + 1;
      FUN_00923370(param_1,*(undefined4 *)(lVar2 + 0x644 + uVar3 * 0x2af0),0);
      uVar1 = *(uint *)(lVar2 + 0x270c + uVar3 * 0x2af0);
      if (uVar1 != 0xffffffff) {
        uVar3 = (ulong)((uVar1 & 0x1fff) * DAT_02689800);
        FUN_00656ed0((DAT_026897f8 + uVar3) -
                     ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar3)));
        return;
      }
    }
  }
  return;
}

