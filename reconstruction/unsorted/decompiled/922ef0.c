
void FUN_00922ef0(uint param_1,int param_2)

{
  short *psVar1;
  int iVar2;
  long lVar3;
  long lVar4;
  ulong uVar5;
  
  uVar5 = (ulong)param_1 & 0xffff;
  iVar2 = *(int *)(DAT_0273eb80 + uVar5 * 2 + 0x36);
  lVar4 = (long)iVar2;
  if (iVar2 != param_2) {
    if (param_2 != -1) {
      lVar3 = *(long *)(DAT_0273ea80 + 8);
      if (iVar2 != -1) {
        if (*(int *)(DAT_0273eb80 + lVar4 * 2 + 4) != -1) {
          FUN_0091b2a0(iVar2,0xffffffff);
          psVar1 = DAT_0273eb80 + lVar4 * 2 + 4;
          psVar1[0] = -1;
          psVar1[1] = -1;
        }
        psVar1 = DAT_0273eb80 + lVar4 * 2 + 2;
        psVar1[0] = -1;
        psVar1[1] = -1;
        psVar1 = DAT_0273eb80 + uVar5 * 2 + 0x36;
        psVar1[0] = -1;
        psVar1[1] = -1;
        *DAT_0273eb80 = *DAT_0273eb80 + -1;
      }
      *(int *)(DAT_0273eb80 + uVar5 * 2 + 0x36) = param_2;
      *(uint *)(DAT_0273eb80 + (long)param_2 * 2 + 2) = param_1;
      *DAT_0273eb80 = *DAT_0273eb80 + 1;
      FUN_00923010(param_2,*(undefined4 *)(lVar3 + 0x644 + uVar5 * 0x2af0));
      return;
    }
    if (*(int *)(DAT_0273eb80 + lVar4 * 2 + 4) != -1) {
      FUN_0091b2a0(iVar2,0xffffffff);
      psVar1 = DAT_0273eb80 + lVar4 * 2 + 4;
      psVar1[0] = -1;
      psVar1[1] = -1;
    }
    psVar1 = DAT_0273eb80 + lVar4 * 2 + 2;
    psVar1[0] = -1;
    psVar1[1] = -1;
    psVar1 = DAT_0273eb80 + uVar5 * 2 + 0x36;
    psVar1[0] = -1;
    psVar1[1] = -1;
    *DAT_0273eb80 = *DAT_0273eb80 + -1;
  }
  return;
}

