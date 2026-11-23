
undefined8 FUN_00587710(void)

{
  char *pcVar1;
  char *pcVar2;
  long lVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  char *pcVar6;
  int iVar7;
  
  uVar5 = 0;
  if (DAT_026bc510 != 0) {
    iVar7 = -1;
    lVar3 = 0;
    pcVar6 = (char *)(DAT_026bc510 + -0x30);
    do {
      iVar7 = iVar7 + 1;
      if (0 < iVar7) {
        pcVar1 = (char *)0x0;
        break;
      }
      pcVar1 = pcVar6 + 0x30;
      pcVar2 = pcVar6 + 0x30;
      pcVar6 = pcVar1;
    } while (*pcVar2 == '\0');
    do {
      pcVar6 = pcVar1;
      if (pcVar6 == (char *)0x0) goto LAB_00587786;
      pcVar1 = (char *)0x0;
    } while (*pcVar6 != '\x03');
    lVar3 = *(long *)(pcVar6 + 1);
LAB_00587786:
    uVar5 = 0;
    if (lVar3 != 0) {
      iVar7 = -1;
      uVar4 = 0;
      pcVar6 = (char *)(DAT_026bc510 + -0x30);
      do {
        iVar7 = iVar7 + 1;
        if (0 < iVar7) {
          pcVar1 = (char *)0x0;
          break;
        }
        pcVar1 = pcVar6 + 0x30;
        pcVar2 = pcVar6 + 0x30;
        pcVar6 = pcVar1;
      } while (*pcVar2 == '\0');
      do {
        pcVar6 = pcVar1;
        uVar5 = 0;
        if (pcVar6 == (char *)0x0) goto LAB_005877fd;
        pcVar1 = (char *)0x0;
      } while (lVar3 != *(long *)(pcVar6 + 1));
      uVar5 = uVar4;
      if (((*pcVar6 == '\x03') && (*(long *)(pcVar6 + 0x10) != 0)) && (pcVar6[0x18] != '\0')) {
        uVar5 = *(undefined8 *)(pcVar6 + 0x20);
      }
    }
  }
LAB_005877fd:
  if (*DAT_01a1f100 != *DAT_01a1f100) {
    uVar5 = thunk_FUN_012aa7f6();
    return uVar5;
  }
  return uVar5;
}

