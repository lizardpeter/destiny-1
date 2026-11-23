
void FUN_00300790(int param_1,int param_2,int param_3)

{
  long lVar1;
  int iVar2;
  
  lVar1 = DAT_02689540;
  iVar2 = *(int *)(DAT_02689540 + 0x60);
  if (*(int *)(DAT_02689540 + 0x60) < param_1) {
    iVar2 = param_1;
  }
  *(int *)(DAT_02689540 + 0x60) = iVar2;
  iVar2 = *(int *)(lVar1 + 100);
  if (*(int *)(lVar1 + 100) < param_2) {
    iVar2 = param_2;
  }
  *(int *)(lVar1 + 100) = iVar2;
  iVar2 = *(int *)(lVar1 + 0x68);
  if (*(int *)(lVar1 + 0x68) < param_3) {
    iVar2 = param_3;
  }
  *(int *)(lVar1 + 0x68) = iVar2;
  return;
}

