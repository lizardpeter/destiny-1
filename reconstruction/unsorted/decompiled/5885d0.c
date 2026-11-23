
void FUN_005885d0(char param_1)

{
  long *plVar1;
  bool bVar2;
  char cVar3;
  byte bVar4;
  uint uVar5;
  long lVar6;
  char *pcVar7;
  uint uVar8;
  long lVar9;
  
  lVar6 = FUN_00557c40(&DAT_026bc270);
  cVar3 = FUN_00906f70();
  bVar4 = 0;
  if (cVar3 == '\0') {
    bVar4 = FUN_00752150(3);
    bVar4 = bVar4 ^ 1;
  }
  if ((lVar6 != 0) && (bVar4 == 0)) {
    FUN_00575d10();
    pcVar7 = (char *)FUN_00057f80(lVar6);
    if (*pcVar7 != '\0') {
      lVar9 = 0;
      do {
        (**(code **)(**(long **)((long)&PTR_DAT_0193ffc0 + lVar9) + 0x10))();
        lVar9 = lVar9 + 0x10;
      } while ((int)lVar9 != 0x150);
      FUN_0006c520(lVar6);
    }
  }
  if (((lVar6 != 0 && param_1 == '\x01') && bVar4 == 0) &&
     (pcVar7 = (char *)FUN_0019e750(lVar6), *pcVar7 != '\0')) {
    cVar3 = FUN_00906f70();
    if (cVar3 == '\0') {
      FUN_00021860(&DAT_026bc270);
    }
    lVar6 = FUN_0058b140();
    cVar3 = FUN_00906e00();
    uVar5 = 0xffffffff;
    if (cVar3 != '\0') {
      uVar5 = FUN_005916f0();
    }
    uVar8 = uVar5 & 3;
    if ((int)uVar5 < 0) {
      lVar9 = 0;
      do {
        plVar1 = *(long **)((long)&PTR_DAT_0193ffc0 + lVar9);
        cVar3 = (**(code **)(*plVar1 + 0x40))
                          (plVar1,(int)*(char *)(lVar6 + 4),(int)*(char *)(lVar6 + 5),
                           *(undefined1 *)(lVar6 + 7));
        if (cVar3 != '\0') {
          FUN_00001f70();
          (**(code **)(*plVar1 + 0x30))(plVar1);
        }
        lVar9 = lVar9 + 0x10;
      } while ((int)lVar9 != 0x150);
    }
    else {
      lVar9 = 8;
      do {
        plVar1 = *(long **)(lVar9 + 0x193ffb8);
        cVar3 = (**(code **)(*plVar1 + 0x40))
                          (plVar1,(int)*(char *)(lVar6 + 4),(int)*(char *)(lVar6 + 5),
                           *(undefined1 *)(lVar6 + 7));
        if (cVar3 != '\0') {
          cVar3 = FUN_00001f70();
          if (cVar3 != '\0') {
            bVar2 = uVar8 == 3;
            switch(*(undefined4 *)((long)&PTR_DAT_0193ffc0 + lVar9)) {
            case 0:
              bVar2 = uVar8 == 0;
              break;
            case 1:
              bVar2 = uVar8 == 1;
              break;
            case 2:
              bVar2 = uVar8 == 2;
              break;
            case 3:
              break;
            case 4:
              goto switchD_0058873e_caseD_4;
            default:
              goto switchD_0058873e_default;
            }
            if (!bVar2) goto switchD_0058873e_default;
          }
switchD_0058873e_caseD_4:
          (**(code **)(*plVar1 + 0x30))(plVar1);
        }
switchD_0058873e_default:
        lVar9 = lVar9 + 0x10;
      } while ((int)lVar9 != 0x158);
    }
  }
  return;
}

