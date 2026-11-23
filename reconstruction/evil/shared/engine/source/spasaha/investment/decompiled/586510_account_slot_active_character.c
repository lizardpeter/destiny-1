
undefined8 FUN_00586510(long param_1,long *param_2)

{
  char *pcVar1;
  char *pcVar2;
  int iVar3;
  char *pcVar4;
  
  iVar3 = -1;
  pcVar4 = (char *)(param_1 + -0x30);
  do {
    iVar3 = iVar3 + 1;
    pcVar2 = (char *)0x0;
    if (0 < iVar3) break;
    pcVar1 = pcVar4 + 0x30;
    pcVar2 = pcVar4 + 0x30;
    pcVar4 = pcVar4 + 0x30;
  } while (*pcVar1 == '\0');
  do {
    pcVar4 = pcVar2;
    if (pcVar4 == (char *)0x0) {
      return 0;
    }
    pcVar2 = (char *)0x0;
  } while (*param_2 != *(long *)(pcVar4 + 1));
  if (((*pcVar4 == '\x03') && (*(long *)(pcVar4 + 0x10) != 0)) && (pcVar4[0x18] != '\0')) {
    return *(undefined8 *)(pcVar4 + 0x20);
  }
  return 0;
}

