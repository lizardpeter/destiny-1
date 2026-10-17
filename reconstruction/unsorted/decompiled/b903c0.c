
undefined8 FUN_00b903c0(long param_1,int *param_2)

{
  char cVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  bool bVar6;
  undefined8 in_RAX;
  undefined7 uVar7;
  undefined7 extraout_var;
  int iVar8;
  
  iVar3 = param_2[2];
  iVar4 = *param_2;
  iVar5 = param_2[1];
  cVar1 = (char)param_2[6];
  iVar8 = *(int *)(param_1 + 0xec);
  bVar6 = false;
  if (iVar8 == 0) {
LAB_00b90411:
    iVar8 = 0;
  }
  else if (iVar5 < *(int *)(param_1 + 0xf0)) {
    *(undefined4 *)(param_1 + 0xec) = 0;
    *(undefined4 *)(param_1 + 0xf0) = 0xffffffff;
    *(undefined8 *)(param_1 + 0xf4) = 0;
    bVar6 = true;
    goto LAB_00b90411;
  }
  cVar2 = *(char *)(param_1 + 0xfc);
  uVar7 = (undefined7)((ulong)in_RAX >> 8);
  if ((((cVar2 == cVar1) && (*(int *)(param_1 + 0xe4) == iVar4)) &&
      (*(int *)(param_1 + 0xe8) == iVar5)) && (iVar8 == iVar3)) {
    if (!bVar6) goto LAB_00b904bc;
  }
  else {
    *(char *)(param_1 + 0xfc) = cVar1;
    *(int *)(param_1 + 0xe4) = iVar4;
    *(int *)(param_1 + 0xe8) = iVar5;
    if (cVar2 == '\0' || (iVar3 == 0 || cVar1 == '\0')) {
      *(undefined4 *)(param_1 + 0xec) = 0;
      *(undefined4 *)(param_1 + 0xf0) = 0xffffffff;
      *(undefined8 *)(param_1 + 0xf4) = 0;
    }
    else {
      *(int *)(param_1 + 0xec) = iVar3;
      *(int *)(param_1 + 0xf0) = iVar5;
      if (iVar3 == 1) {
        *(undefined8 *)(param_1 + 0xf4) = *(undefined8 *)(param_2 + 4);
      }
      else {
        *(undefined8 *)(param_1 + 0xf4) = 0;
      }
    }
  }
  FUN_00b8f880();
  uVar7 = extraout_var;
LAB_00b904bc:
  return CONCAT71(uVar7,1);
}

