
undefined8 FUN_005862e0(long param_1)

{
  char *pcVar1;
  char *pcVar2;
  int iVar3;
  undefined8 uVar4;
  char *pcVar5;
  bool bVar6;
  long local_28;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  bVar6 = false;
  if ((*(char *)(param_1 + 0x41c) == '\0') && (FUN_00244ee0(&local_28), local_28 != 0)) {
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
      if (pcVar5 == (char *)0x0) goto LAB_00586375;
      pcVar2 = (char *)0x0;
    } while (local_28 != *(long *)(pcVar5 + 1));
    if (*pcVar5 == '\x03') {
      bVar6 = *(long *)(pcVar5 + 0x10) != 0;
    }
  }
LAB_00586375:
  if (*DAT_01a1f100 != local_20) {
    uVar4 = thunk_FUN_012aa7f6();
    return uVar4;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),bVar6);
}

