
void FUN_00639d30(int *param_1)

{
  int iVar1;
  int iVar2;
  int iVar3;
  
  if ((char)param_1[0x43] == '\0') {
    iVar2 = 0;
    do {
      iVar3 = FUN_00639e00(param_1,*param_1);
      if (iVar3 == 0) {
        return;
      }
      iVar1 = *param_1;
      if (((iVar1 == 5) || (iVar1 == 3)) || (iVar1 == 1)) {
        FUN_0063c370(param_1 + 0x35);
      }
      *param_1 = iVar3;
      if (iVar3 == 2) {
        FUN_0063a700(param_1);
      }
      iVar2 = iVar2 + 1;
    } while (iVar2 < 8);
  }
  else {
    iVar2 = *param_1;
    if ((iVar2 != 8) &&
       (((iVar2 != 3 && (iVar2 != 1)) || (iVar2 = FUN_0063c730(param_1 + 0x35), iVar2 != 1)))) {
      FUN_0063a0d0(param_1);
      return;
    }
  }
  return;
}

