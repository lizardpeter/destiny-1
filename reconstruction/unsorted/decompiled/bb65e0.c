
void FUN_00bb65e0(long param_1)

{
  int iVar1;
  char cVar2;
  
  if (((*(int *)(param_1 + 8) != 1) || (*(int *)(param_1 + 0x44) == 0)) &&
     (iVar1 = *(int *)(param_1 + 0x48), iVar1 != 0)) {
    cVar2 = FUN_0023b570();
    if (cVar2 == '\0') {
      if ((*(int *)(param_1 + 8) != 1) || (*(int *)(param_1 + 0x44) == 0)) {
        FUN_008dd4e0();
        *(int *)(param_1 + 0x44) = iVar1;
      }
    }
    else {
      *(int *)(param_1 + 0x4c) = iVar1;
    }
    FUN_00ae8e70();
    *(undefined4 *)(param_1 + 0x48) = 0;
  }
  return;
}

