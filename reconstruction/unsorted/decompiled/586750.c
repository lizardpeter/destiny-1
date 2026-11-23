
long FUN_00586750(long param_1,long param_2)

{
  char *pcVar1;
  char *pcVar2;
  long lVar3;
  long lVar4;
  bool bVar5;
  long lVar6;
  long lVar7;
  long lVar8;
  long lVar9;
  int iVar10;
  long lVar11;
  bool bVar12;
  char *pcVar13;
  long local_40;
  long local_38;
  
  lVar8 = *DAT_01a1f100;
  local_38 = FUN_00001df0();
  iVar10 = -1;
  local_40 = 0;
  pcVar13 = (char *)(param_1 + -0x30);
  do {
    iVar10 = iVar10 + 1;
    if (0 < iVar10) {
      pcVar1 = (char *)0x0;
      break;
    }
    pcVar1 = pcVar13 + 0x30;
    pcVar2 = pcVar13 + 0x30;
    pcVar13 = pcVar1;
  } while (*pcVar2 == '\0');
  do {
    pcVar13 = pcVar1;
    if (pcVar13 == (char *)0x0) goto LAB_005867c6;
    pcVar1 = (char *)0x0;
  } while (*pcVar13 != '\x03');
  local_40 = *(long *)(pcVar13 + 1);
LAB_005867c6:
  lVar7 = local_38;
  if (local_40 != 0) {
    lVar6 = local_40;
    do {
      if (local_38 != 0) break;
      iVar10 = -1;
      pcVar13 = (char *)(param_1 + -0x30);
      do {
        iVar10 = iVar10 + 1;
        lVar11 = 0;
        if (0 < iVar10) {
          pcVar1 = (char *)0x0;
          break;
        }
        pcVar2 = pcVar13 + 0x30;
        pcVar1 = pcVar13 + 0x30;
        pcVar13 = pcVar13 + 0x30;
      } while (*pcVar2 == '\0');
      do {
        pcVar13 = pcVar1;
        if (pcVar13 == (char *)0x0) goto LAB_00586870;
        pcVar1 = (char *)0x0;
      } while (local_40 != *(long *)(pcVar13 + 1));
      if (((*pcVar13 == '\x03') && (*(long *)(pcVar13 + 0x10) != 0)) &&
         (lVar11 = 0, pcVar13[0x18] != '\0')) {
        lVar11 = *(long *)(pcVar13 + 0x20);
      }
LAB_00586870:
      lVar9 = lVar6;
      lVar3 = local_40;
      lVar4 = lVar6;
      if (lVar11 != param_2) {
        iVar10 = -1;
        pcVar13 = (char *)(param_1 + -0x30);
        do {
          iVar10 = iVar10 + 1;
          bVar12 = false;
          pcVar1 = (char *)0x0;
          if (0 < iVar10) break;
          pcVar2 = pcVar13 + 0x30;
          pcVar1 = pcVar13 + 0x30;
          pcVar13 = pcVar13 + 0x30;
        } while (*pcVar2 == '\0');
LAB_005868b0:
        pcVar13 = pcVar1;
        lVar6 = lVar7;
        lVar9 = 0;
        lVar3 = 0;
        lVar4 = local_38;
        if (pcVar13 != (char *)0x0) {
          pcVar1 = (char *)0x0;
          if (*pcVar13 == '\x03') {
            if (bVar12) {
              lVar9 = *(long *)(pcVar13 + 1);
              lVar3 = lVar9;
              goto LAB_005868e4;
            }
            bVar5 = true;
            if (local_40 != *(long *)(pcVar13 + 1)) {
              bVar5 = bVar12;
            }
            bVar12 = bVar5;
            pcVar1 = (char *)0x0;
          }
          goto LAB_005868b0;
        }
      }
LAB_005868e4:
      local_38 = lVar4;
      local_40 = lVar3;
      lVar7 = lVar6;
      lVar6 = lVar9;
    } while (local_40 != 0);
  }
  if (*DAT_01a1f100 != lVar8) {
    lVar8 = thunk_FUN_012aa7f6();
    return lVar8;
  }
  return lVar7;
}

