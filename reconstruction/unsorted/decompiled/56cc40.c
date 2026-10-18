
long FUN_0056cc40(undefined8 param_1,long *param_2,short *param_3,long *param_4,undefined4 param_5,
                 undefined4 param_6)

{
  char cVar1;
  long lVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  long lVar5;
  long lVar6;
  int iVar7;
  undefined1 local_170 [320];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  lVar2 = (long)*param_3;
  iVar7 = (int)*param_3 + (int)param_3[1];
  lVar5 = lVar2;
  do {
    if (iVar7 <= (int)lVar5) goto LAB_0056ccb0;
    lVar6 = param_2[2] * lVar5;
    lVar5 = lVar5 + 1;
  } while (*(long *)(*param_2 + lVar6) != *param_4);
  lVar6 = *param_2 + lVar6;
  if (lVar6 == 0) {
LAB_0056ccb0:
    do {
      if (iVar7 <= (int)lVar2) goto LAB_0056ccdf;
      lVar6 = param_2[2] * lVar2;
      lVar2 = lVar2 + 1;
    } while (*(long *)(*param_2 + lVar6) != 0);
    lVar6 = *param_2 + lVar6;
    if (lVar6 == 0) {
LAB_0056ccdf:
      cVar1 = FUN_000e4d70(8,4);
      lVar6 = 0;
      if (cVar1 != '\0') {
        if ((DAT_026bad50 == '\0') && (iVar7 = thunk_FUN_012aa7d6(&DAT_026bad50), iVar7 != 0)) {
          DAT_026bad48 = FUN_000e4a10(s_networking_investment_server_obj_0163c9d9);
          thunk_FUN_012aa7e6(&DAT_026bad50);
        }
        uVar3 = FUN_000e9fa0(param_5);
        uVar4 = FUN_000e9fa0(param_6);
        FUN_01008290(local_170,s_networking_investment_server_obj_0163c9d9,uVar3,uVar4,*param_4);
        FUN_000e4aa0(DAT_026bad48,local_170);
      }
    }
    else {
      thunk_FUN_002c8840((int)param_2[3],lVar6);
    }
  }
  if (*DAT_01a1f100 != local_30) {
    lVar5 = thunk_FUN_012aa7f6();
    return lVar5;
  }
  return lVar6;
}

