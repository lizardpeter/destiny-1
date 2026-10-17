
void FUN_0057f880(long *param_1)

{
  long lVar1;
  ushort *puVar2;
  int iVar3;
  long *plVar4;
  
  plVar4 = (long *)(DAT_026bc448 + 0x14);
  puVar2 = (ushort *)(DAT_026bc448 + 0x88);
  iVar3 = 0;
  do {
    if (0 < iVar3) goto LAB_0057f8df;
    puVar2 = puVar2 + 1;
    iVar3 = iVar3 + 1;
    lVar1 = *plVar4;
    plVar4 = plVar4 + 1;
  } while (*param_1 != lVar1);
  if ((iVar3 != 0) && (0 < *(int *)(DAT_026bc448 + 0x20))) {
    iVar3 = 0;
    do {
      if ((*puVar2 & *(ushort *)(param_1 + 1)) != 0) {
        *(int *)((long)param_1 + 0xc) = iVar3;
        return;
      }
      puVar2 = puVar2 + 0x34;
      iVar3 = iVar3 + 1;
    } while (iVar3 < *(int *)(DAT_026bc448 + 0x20));
  }
LAB_0057f8df:
  *(undefined4 *)((long)param_1 + 0xc) = 0xffffffff;
  return;
}

