
long FUN_005864b0(long param_1,long *param_2)

{
  char *pcVar1;
  char *pcVar2;
  int iVar3;
  long lVar4;
  char *pcVar5;
  
  iVar3 = -1;
  pcVar5 = (char *)(param_1 + -0x30);
  do {
    iVar3 = iVar3 + 1;
    pcVar2 = (char *)0x0;
    if (0 < iVar3) break;
    pcVar1 = pcVar5 + 0x30;
    pcVar2 = pcVar5 + 0x30;
    pcVar5 = pcVar5 + 0x30;
  } while (*pcVar1 == '\0');
  do {
    pcVar5 = pcVar2;
    if (pcVar5 == (char *)0x0) {
      return 0;
    }
    pcVar2 = (char *)0x0;
  } while (*param_2 != *(long *)(pcVar5 + 1));
  if ((*pcVar5 == '\x03') && (*(long *)(pcVar5 + 0x10) != 0)) {
    lVar4 = 0;
    if (pcVar5[0x18] != '\0') {
      lVar4 = *(long *)(pcVar5 + 0x10);
    }
    return lVar4;
  }
  return 0;
}

