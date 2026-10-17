
void FUN_00587880(void)

{
  char *pcVar1;
  char *pcVar2;
  long *plVar3;
  char *pcVar4;
  int iVar5;
  undefined8 local_20;
  long local_18;
  
  plVar3 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  local_20 = 0;
  if (DAT_026bc510 != 0) {
    iVar5 = -1;
    local_20 = 0;
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
      if (pcVar4 == (char *)0x0) goto LAB_005878f6;
      pcVar1 = (char *)0x0;
    } while (*pcVar4 != '\x03');
    local_20 = *(undefined8 *)(pcVar4 + 1);
  }
LAB_005878f6:
  FUN_00945ca0(&local_20);
  if (*plVar3 != local_18) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

