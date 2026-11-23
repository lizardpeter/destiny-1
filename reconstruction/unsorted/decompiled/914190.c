
void FUN_00914190(int *param_1,undefined4 param_2,undefined8 param_3)

{
  char cVar1;
  int iVar2;
  
  cVar1 = FUN_0063b470(param_3);
  iVar2 = -1;
  if (cVar1 == '\0') {
    iVar2 = FUN_0063fb20(param_2,param_3);
  }
  if (*param_1 != -1) {
    FUN_0063fc10();
  }
  *param_1 = iVar2;
  return;
}

