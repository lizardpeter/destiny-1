
void FUN_00585f10(char *param_1)

{
  char *pcVar1;
  long lVar2;
  long *plVar3;
  long *plVar4;
  char *pcVar5;
  int iVar6;
  long *plVar7;
  char *pcVar8;
  
  plVar3 = DAT_01a1f100;
  lVar2 = *DAT_01a1f100;
  plVar4 = (long *)FUN_0058b960();
  if (plVar4 != (long *)0x0) {
    plVar7 = (long *)0x0;
    if ((char)plVar4[7] != '\0') {
      plVar7 = plVar4;
    }
    if (plVar7 != (long *)0x0) {
      iVar6 = -1;
      pcVar8 = param_1 + -0x30;
      do {
        iVar6 = iVar6 + 1;
        pcVar5 = (char *)0x0;
        if (0 < iVar6) break;
        pcVar5 = pcVar8 + 0x30;
        pcVar1 = pcVar8 + 0x30;
        pcVar8 = pcVar5;
      } while (*pcVar1 == '\0');
      do {
        if (pcVar5 == (char *)0x0) {
          iVar6 = -1;
          pcVar8 = param_1 + -0x30;
          goto LAB_00585fc0;
        }
        plVar4 = (long *)(pcVar5 + 1);
        pcVar5 = (char *)0x0;
      } while (*plVar7 != *plVar4);
      goto LAB_00585fdc;
    }
  }
  if (*param_1 != '\0') {
    FUN_00586180(param_1,param_1);
  }
  goto LAB_00585fdc;
  while (pcVar5 = pcVar8 + 0x30, pcVar8 = pcVar8 + 0x30, *pcVar5 != '\0') {
LAB_00585fc0:
    iVar6 = iVar6 + 1;
    if (0 < iVar6) goto LAB_00585fdc;
  }
  FUN_00587010();
LAB_00585fdc:
  if (*plVar3 != lVar2) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

