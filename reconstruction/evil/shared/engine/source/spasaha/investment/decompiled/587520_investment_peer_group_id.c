
undefined8 FUN_00587520(void)

{
  char *pcVar1;
  char *pcVar2;
  undefined8 uVar3;
  char *pcVar4;
  int iVar5;
  
  uVar3 = 0;
  if (DAT_026bc510 != 0) {
    iVar5 = -1;
    pcVar4 = (char *)(DAT_026bc510 + -0x30);
    do {
      iVar5 = iVar5 + 1;
      if (0 < iVar5) {
        pcVar1 = (char *)0x0;
        break;
      }
      pcVar1 = pcVar4 + 0x30;
      pcVar2 = pcVar4 + 0x30;
      pcVar4 = pcVar1;
    } while (*pcVar2 == '\0');
    do {
      pcVar4 = pcVar1;
      if (pcVar4 == (char *)0x0) {
        return 0;
      }
      pcVar1 = (char *)0x0;
    } while (*pcVar4 != '\x03');
    uVar3 = *(undefined8 *)(pcVar4 + 1);
  }
  return uVar3;
}

