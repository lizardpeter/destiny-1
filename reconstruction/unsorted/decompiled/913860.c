
void FUN_00913860(uint param_1)

{
  undefined4 *puVar1;
  int iVar2;
  long lVar3;
  long lVar4;
  long lVar5;
  long lVar6;
  
  lVar3 = *DAT_01a1f100;
  lVar6 = (ulong)(param_1 & 0xffff) * 0x2af0;
  lVar4 = *(long *)(DAT_0273ea80 + 8);
  iVar2 = *(int *)(lVar4 + 8 + lVar6);
  lVar5 = lVar4;
  if (iVar2 != -1) {
    puVar1 = (undefined4 *)(lVar4 + 8 + lVar6);
    if ((*(char *)(DAT_0273ea90 + 0xa8) == '\0') ||
       (*(long *)(lVar4 + 0x620 + lVar6) != *(long *)(DAT_0273ea90 + 0xa9))) {
      FUN_00bb97f0();
      FUN_00ba8010(*puVar1,0xffffffff);
    }
    else {
      FUN_00bb9700(iVar2,1);
    }
    *puVar1 = 0xffffffff;
    lVar5 = *(long *)(DAT_0273ea80 + 8);
  }
  if (*(char *)(DAT_0273ea90 + 0xa8) != '\0') {
    if (*(long *)(lVar5 + 0x620 + lVar6) == *(long *)(DAT_0273ea90 + 0xa9)) {
      FUN_00649330(param_1);
    }
  }
  FUN_0090cfc0(lVar4 + lVar6);
  FUN_0063fce0(*(undefined4 *)(lVar4 + 0x2858 + lVar6));
  *(undefined4 *)(lVar4 + 0x2858 + lVar6) = 0xffffffff;
  FUN_00911c50(param_1,0xffffffff,0,0);
  FUN_00922ef0(param_1,0xffffffff);
  FUN_00923080(param_1,0xffffffff);
  FUN_00923590(param_1);
  FUN_0090e120(0);
  FUN_005bdd20(param_1);
  FUN_00302a60(*(undefined4 *)(lVar4 + 4 + lVar6));
  FUN_00074760(DAT_0273ea80,param_1);
  FUN_008dd4e0(param_1);
  FUN_00bcf8f0(param_1);
  FUN_008e3d20(param_1);
  if (*DAT_01a1f100 == lVar3) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

