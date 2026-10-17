
long FUN_0056cfe0(undefined8 param_1,long *param_2,short *param_3,long *param_4,undefined4 param_5,
                 undefined4 param_6)

{
  char cVar1;
  int iVar2;
  long lVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  long lVar6;
  undefined1 local_170 [320];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  lVar3 = (long)*param_3;
  do {
    if ((int)*param_3 + (int)param_3[1] <= (int)lVar3) goto LAB_0056d044;
    lVar6 = param_2[2] * lVar3;
    lVar3 = lVar3 + 1;
  } while (*(long *)(*param_2 + lVar6) != *param_4);
  lVar6 = *param_2 + lVar6;
  if (lVar6 == 0) {
LAB_0056d044:
    cVar1 = FUN_000e4d70(8,4);
    lVar6 = 0;
    if (cVar1 != '\0') {
      if (DAT_026bad40 == '\0') {
        iVar2 = thunk_FUN_012aa7d6(&DAT_026bad40);
        if (iVar2 != 0) {
          DAT_026bad38 = FUN_000e4a10(s_networking_investment_server_obj_0163c94a);
          thunk_FUN_012aa7e6(&DAT_026bad40);
        }
      }
      uVar4 = FUN_000e9fa0(param_5);
      uVar5 = FUN_000e9fa0(param_6);
      FUN_01008290(local_170,s_networking_investment_server_obj_0163c94a,uVar4,uVar5,*param_4);
      FUN_000e4aa0(DAT_026bad38,local_170);
    }
  }
  if (*DAT_01a1f100 == local_30) {
    return lVar6;
  }
  lVar3 = thunk_FUN_012aa7f6();
  return lVar3;
}

