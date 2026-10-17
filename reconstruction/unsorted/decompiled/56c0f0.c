
undefined1
FUN_0056c0f0(long param_1,undefined4 param_2,long *param_3,int param_4,byte *param_5,
            undefined8 param_6,undefined4 param_7,undefined8 param_8)

{
  long lVar1;
  char cVar2;
  undefined1 uVar3;
  int iVar4;
  int iVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined4 uVar8;
  long lVar9;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar9 = 0;
  uVar3 = 0;
  while ((*(char *)(param_1 + 0x60 + lVar9) != (char)param_2 ||
         (*(long *)(param_1 + 0x80 + lVar9) != *param_3))) {
    lVar9 = lVar9 + 0x40;
    if ((int)lVar9 == 0x4040) {
LAB_0056c423:
      if (*DAT_01a1f100 != local_38) {
        uVar3 = thunk_FUN_012aa7f6();
        return uVar3;
      }
      return uVar3;
    }
  }
  cVar2 = *(char *)(param_1 + 0x88 + lVar9);
  if (cVar2 == '\x03') {
    if ((*param_5 & 1) == 0) {
      uVar6 = FUN_00021860(&DAT_026bc270);
      iVar4 = *(int *)(param_1 + 0x9c + lVar9) + 1;
      uVar3 = 1;
      if (iVar4 != param_4) {
        cVar2 = FUN_000e4d70(8,4);
        if (cVar2 != '\0') {
          if ((DAT_026bad00 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_026bad00), iVar5 != 0)) {
            DAT_026bacf8 = FUN_000e4a10(s_networking_investment_server_obj_0163c682);
            thunk_FUN_012aa7e6(&DAT_026bad00);
          }
          lVar1 = *param_3;
          uVar7 = FUN_000e9fa0(param_2);
          FUN_01008290(local_178,s_networking_investment_server_obj_0163c682,lVar1,uVar7,iVar4,
                       param_4);
          FUN_000e4aa0(DAT_026bacf8,local_178);
        }
        FUN_00575990(uVar6,6);
        uVar3 = 0;
      }
      *(int *)(param_1 + 0x9c + lVar9) = param_4;
    }
    else {
      iVar4 = FUN_00280b70(param_2);
      if (iVar4 == 1) {
        FUN_00510e40(param_2,param_3);
      }
      FUN_0056c460(param_1,param_1 + 0x60 + lVar9,param_6,param_7);
LAB_0056c1e8:
      *(int *)(param_1 + 0x9c + lVar9) = param_4;
      uVar3 = 1;
    }
  }
  else if (cVar2 == '\x02') {
    FUN_00543ee0(param_1 + 0x94 + lVar9);
    if ((*param_5 & 1) != 0) {
      *(undefined1 *)(param_1 + 0x88 + lVar9) = 3;
      *(undefined1 *)(param_1 + 0x89 + lVar9) = 0;
      goto LAB_0056c1e8;
    }
    cVar2 = FUN_000e4d70(8,3);
    uVar3 = 0;
    if (cVar2 != '\0') {
      if ((DAT_026bacf0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026bacf0), iVar4 != 0)) {
        DAT_026bacec = FUN_000e4a10(s_networking_investment_server_obj_0163c5f8);
        thunk_FUN_012aa7e6(&DAT_026bacf0);
      }
      uVar6 = FUN_000e9fa0(param_2);
      FUN_01008290(local_178,s_networking_investment_server_obj_0163c5f8,uVar6,*param_3);
      uVar8 = DAT_026bacec;
      goto LAB_0056c409;
    }
  }
  else {
    cVar2 = FUN_000e4d70(8,4);
    uVar3 = 0;
    if (cVar2 != '\0') {
      if ((DAT_026bad10 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026bad10), iVar4 != 0)) {
        DAT_026bad08 = FUN_000e4a10(s_networking_investment_server_obj_0163c745);
        thunk_FUN_012aa7e6(&DAT_026bad10);
      }
      uVar6 = FUN_000e9fa0(param_2);
      FUN_01008290(local_178,s_networking_investment_server_obj_0163c745,uVar6,*param_3,
                   (int)*(char *)(param_1 + lVar9 + 0x88));
      uVar8 = DAT_026bad08;
LAB_0056c409:
      uVar3 = 0;
      FUN_000e4aa0(uVar8,local_178);
    }
  }
  FUN_0056e270(param_2,param_3,param_8);
  goto LAB_0056c423;
}

