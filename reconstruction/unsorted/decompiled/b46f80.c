
undefined1 FUN_00b46f80(int param_1,int param_2,undefined1 param_3)

{
  long lVar1;
  int *piVar2;
  int iVar3;
  long lVar4;
  char cVar5;
  ulong uVar6;
  long lVar7;
  long lVar8;
  int iVar9;
  long lVar10;
  
  lVar4 = DAT_0282eda0;
  uVar6 = (ulong)param_1;
  iVar3 = *(int *)(DAT_0282eda0 + 0xd0 + uVar6 * 0x48);
  if (iVar3 != param_2) {
    iVar9 = -1;
    if ((*(char *)(DAT_0282eda0 + 0x1761) != '\0') &&
       ((*(byte *)(DAT_0282eda0 + 0xd8 + uVar6 * 0x48) & 2) != 0)) {
      iVar9 = *(int *)(DAT_0282eda0 + 0xcc + uVar6 * 0x48);
    }
    piVar2 = (int *)(DAT_0282eda0 + 0xd0 + uVar6 * 0x48);
    if (iVar3 != 0) {
      if (iVar9 == -1) {
        lVar10 = (long)*(char *)(DAT_0282eda0 + 0xec + uVar6 * 0x48);
        if (lVar10 != -1) {
          lVar8 = DAT_0282eda0 + 0xec;
          lVar1 = DAT_0282eda0 + 0x1cd0;
          do {
            lVar7 = FUN_000f2220(lVar1);
          } while (lVar7 == 0);
          *(undefined1 *)(lVar7 + 8) = 1;
          *(long *)(lVar7 + 0x10) = lVar10;
          FUN_000f2160(lVar4 + 0x1cc0,lVar7);
          *(undefined1 *)(lVar8 + uVar6 * 0x48) = 0xff;
        }
        FUN_00b49640(DAT_0282eda0 + 0x1d60,uVar6 | 0xbeefcafe00000000,iVar3,param_3);
      }
      else {
        FUN_00b49290(DAT_0282eda0 + 0x1d60);
      }
      *piVar2 = 0;
    }
    lVar4 = DAT_0282eda0;
    if (param_2 != 0) {
      if (iVar9 == -1) {
        cVar5 = FUN_00b49600(DAT_0282eda0 + 0x1d60,uVar6 | 0xbeefcafe00000000,param_2);
        lVar10 = DAT_0282eda0;
        if (cVar5 == '\0') {
          return 0;
        }
        lVar1 = DAT_0282eda0 + 0x1cd0;
        do {
          lVar8 = FUN_000f2220(lVar1);
        } while (lVar8 == 0);
        *(undefined1 *)(lVar8 + 8) = 0;
        *(undefined8 *)(lVar8 + 0x10) = *(undefined8 *)(lVar4 + 0xb8 + uVar6 * 0x48);
        FUN_000f2160(lVar10 + 0x1cc0,lVar8);
      }
      else {
        cVar5 = FUN_00b49210(DAT_0282eda0 + 0x1d60,iVar9,param_2);
        if (cVar5 == '\0') {
          return 0;
        }
      }
      *piVar2 = param_2;
    }
  }
  return 1;
}

