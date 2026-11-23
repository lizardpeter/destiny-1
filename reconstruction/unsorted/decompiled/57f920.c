
void FUN_0057f920(long *param_1)

{
  long lVar1;
  long *plVar2;
  ushort *puVar3;
  int iVar4;
  int iVar5;
  
  iVar5 = *(int *)((long)param_1 + 0xc) + 1;
  puVar3 = (ushort *)((long)iVar5 * 0x68 + 0x88 + DAT_026bc448);
  plVar2 = (long *)(DAT_026bc448 + 0x14);
  iVar4 = 0;
  do {
    if (0 < iVar4) goto LAB_0057f994;
    puVar3 = puVar3 + 1;
    iVar4 = iVar4 + 1;
    lVar1 = *plVar2;
    plVar2 = plVar2 + 1;
  } while (*param_1 != lVar1);
  if (((iVar4 != 0) && (iVar5 != -1)) && (iVar5 < *(int *)(DAT_026bc448 + 0x20))) {
    do {
      if ((*puVar3 & *(ushort *)(param_1 + 1)) != 0) {
        *(int *)((long)param_1 + 0xc) = iVar5;
        return;
      }
      if (iVar5 == -2) break;
      puVar3 = puVar3 + 0x34;
      iVar5 = iVar5 + 1;
    } while (iVar5 < *(int *)(DAT_026bc448 + 0x20));
  }
LAB_0057f994:
  *(undefined4 *)((long)param_1 + 0xc) = 0xffffffff;
  return;
}

