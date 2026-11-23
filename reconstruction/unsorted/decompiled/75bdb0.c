
void FUN_0075bdb0(undefined8 param_1,int param_2)

{
  int iVar1;
  long lVar2;
  int iVar3;
  int iVar4;
  int *piVar5;
  int iVar6;
  long lVar7;
  
  iVar6 = -1;
  piVar5 = DAT_026c96f8;
  do {
    if (iVar6 == 1) {
      iVar6 = -1;
      break;
    }
    iVar6 = iVar6 + 1;
    iVar3 = *piVar5;
    piVar5 = piVar5 + 1;
  } while (iVar3 != param_2);
  piVar5 = DAT_026c96f8 + 2;
  iVar3 = -1;
  do {
    iVar4 = iVar6;
    if (iVar3 == 1) break;
    iVar3 = iVar3 + 1;
    iVar1 = *piVar5;
    piVar5 = piVar5 + 1;
    iVar4 = iVar3;
  } while (iVar1 != param_2);
  lVar7 = 0;
  do {
    iVar6 = -1;
    if ((int)lVar7 == 2) break;
    iVar6 = 0;
    piVar5 = DAT_026c96f8 + lVar7;
    lVar7 = lVar7 + 1;
  } while (*piVar5 != param_2);
  lVar7 = 0;
  do {
    if ((int)lVar7 == 2) {
      iVar3 = 2 - (uint)(iVar4 == 0);
      if (iVar6 == 0) {
        FUN_00775180(iVar3);
        return;
      }
      goto LAB_0075be5b;
    }
    lVar2 = lVar7 + 2;
    lVar7 = lVar7 + 1;
  } while (DAT_026c96f8[lVar2] != param_2);
  iVar3 = 2 - (uint)(iVar4 == 0);
LAB_0075be5b:
  FUN_00772ec0(iVar3);
  return;
}

