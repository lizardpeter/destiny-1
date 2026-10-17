
long FUN_00586430(long param_1,long *param_2)

{
  char *pcVar1;
  char *pcVar2;
  bool bVar3;
  int iVar4;
  bool bVar5;
  char *pcVar6;
  
  iVar4 = -1;
  pcVar6 = (char *)(param_1 + -0x30);
  do {
    iVar4 = iVar4 + 1;
    pcVar2 = (char *)0x0;
    if (0 < iVar4) break;
    pcVar2 = pcVar6 + 0x30;
    pcVar1 = pcVar6 + 0x30;
    pcVar6 = pcVar2;
  } while (*pcVar1 == '\0');
  bVar5 = false;
  while( true ) {
    do {
      pcVar6 = pcVar2;
      if (pcVar6 == (char *)0x0) {
        return 0;
      }
      pcVar2 = (char *)0x0;
    } while (*pcVar6 != '\x03');
    if (bVar5) break;
    bVar3 = true;
    if (*param_2 != *(long *)(pcVar6 + 1)) {
      bVar3 = bVar5;
    }
    pcVar2 = (char *)0x0;
    bVar5 = bVar3;
  }
  return *(long *)(pcVar6 + 1);
}

