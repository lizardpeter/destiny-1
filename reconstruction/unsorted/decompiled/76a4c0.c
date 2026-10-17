
void FUN_0076a4c0(long param_1)

{
  long lVar1;
  char cVar2;
  short sVar3;
  int iVar4;
  long lVar5;
  long *plVar6;
  undefined1 uVar7;
  long lVar8;
  
  lVar5 = FUN_0034e3c0();
  if (*(char *)(lVar5 + 0x82) == '\0') {
    cVar2 = FUN_0025cc10();
    if (cVar2 != '\0') {
      lVar5 = FUN_00574ef0();
      uVar7 = 0;
      if (*(char *)(lVar5 + 300) == '\0') {
        iVar4 = FUN_00775840(0);
        uVar7 = 1;
        if (iVar4 < 2) {
          iVar4 = FUN_007850a0();
          uVar7 = 0;
          if (iVar4 == 0x24) {
            sVar3 = FUN_00777280(0);
            if (sVar3 == *(short *)(param_1 + 0x6400)) {
              uVar7 = *(undefined1 *)(param_1 + 0x6402);
            }
            else {
              plVar6 = (long *)FUN_0025a550();
              lVar5 = (**(code **)(*plVar6 + 0x328))(plVar6);
              *(short *)(param_1 + 0x6400) = sVar3;
              if (lVar5 == 0) {
                uVar7 = 0;
                *(undefined1 *)(param_1 + 0x6402) = 0;
              }
              else {
                lVar8 = 0;
                uVar7 = 1;
                do {
                  if (*(long *)(lVar5 + 8) <= lVar8) {
                    uVar7 = 0;
                    *(undefined1 *)(param_1 + 0x6402) = 0;
                    goto LAB_0076a59d;
                  }
                  lVar1 = lVar8 * 4;
                  lVar8 = lVar8 + 1;
                } while (*(int *)(lVar5 + 0x10 + lVar1 + *(long *)(lVar5 + 0x10) + 0x10) !=
                         DAT_026ca190);
                *(undefined1 *)(param_1 + 0x6402) = 1;
              }
            }
          }
        }
      }
LAB_0076a59d:
      FUN_002459c0(uVar7);
      return;
    }
  }
  return;
}

