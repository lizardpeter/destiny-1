
bool FUN_005805b0(long param_1,undefined8 param_2,long *param_3,undefined8 *param_4)

{
  long lVar1;
  int iVar2;
  int iVar3;
  long *plVar4;
  
  param_4[0xb] = 0;
  param_4[10] = 0;
  param_4[9] = 0;
  param_4[8] = 0;
  param_4[7] = 0;
  param_4[6] = 0;
  param_4[5] = 0;
  param_4[4] = 0;
  param_4[3] = 0;
  param_4[2] = 0;
  param_4[1] = 0;
  *param_4 = 0;
  plVar4 = (long *)(param_1 + 0x28);
  iVar3 = 0;
  do {
    iVar2 = iVar3;
    if (*(int *)(param_1 + 0x20) <= iVar2) {
      return false;
    }
    iVar3 = iVar2 + 1;
    lVar1 = *plVar4;
    plVar4 = plVar4 + 0xd;
  } while (lVar1 != *param_3);
  if (iVar3 != 0) {
    FUN_0057f9d0(param_1,param_2,iVar2);
  }
  return iVar3 != 0;
}

