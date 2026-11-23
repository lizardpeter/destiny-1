
long FUN_00587580(void)

{
  char *pcVar1;
  char *pcVar2;
  long lVar3;
  long lVar4;
  char *pcVar5;
  int iVar6;
  
  lVar4 = 0;
  if (DAT_026bc510 != 0) {
    iVar6 = -1;
    lVar3 = 0;
    pcVar5 = (char *)(DAT_026bc510 + -0x30);
    do {
      iVar6 = iVar6 + 1;
      if (0 < iVar6) {
        pcVar1 = (char *)0x0;
        break;
      }
      pcVar1 = pcVar5 + 0x30;
      pcVar2 = pcVar5 + 0x30;
      pcVar5 = pcVar1;
    } while (*pcVar2 == '\0');
    do {
      pcVar5 = pcVar1;
      if (pcVar5 == (char *)0x0) goto LAB_005875f6;
      pcVar1 = (char *)0x0;
    } while (*pcVar5 != '\x03');
    lVar3 = *(long *)(pcVar5 + 1);
LAB_005875f6:
    lVar4 = 0;
    if (lVar3 != 0) {
      iVar6 = -1;
      pcVar5 = (char *)(DAT_026bc510 + -0x30);
      do {
        iVar6 = iVar6 + 1;
        if (0 < iVar6) {
          pcVar1 = (char *)0x0;
          break;
        }
        pcVar1 = pcVar5 + 0x30;
        pcVar2 = pcVar5 + 0x30;
        pcVar5 = pcVar1;
      } while (*pcVar2 == '\0');
      do {
        pcVar5 = pcVar1;
        lVar4 = 0;
        if (pcVar5 == (char *)0x0) goto LAB_00587670;
        pcVar1 = (char *)0x0;
      } while (lVar3 != *(long *)(pcVar5 + 1));
      lVar4 = 0;
      if (((*pcVar5 == '\x03') && (*(long *)(pcVar5 + 0x10) != 0)) &&
         (lVar4 = 0, pcVar5[0x18] != '\0')) {
        lVar4 = *(long *)(pcVar5 + 0x10);
      }
    }
  }
LAB_00587670:
  if (*DAT_01a1f100 != *DAT_01a1f100) {
    lVar4 = thunk_FUN_012aa7f6();
    return lVar4;
  }
  return lVar4;
}

