
long FUN_0056cb20(long param_1,undefined4 param_2,long *param_3)

{
  char cVar1;
  int iVar2;
  long lVar3;
  undefined8 uVar4;
  undefined1 local_168 [320];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  lVar3 = 0x60;
  while ((*(char *)(param_1 + lVar3) != (char)param_2 ||
         (*(long *)(param_1 + 0x20 + lVar3) != *param_3))) {
    lVar3 = lVar3 + 0x40;
    if ((int)lVar3 == 0x40a0) {
      cVar1 = FUN_000e4d70(8,4);
      param_1 = 0;
      if (cVar1 != '\0') {
        if (DAT_026bad30 == '\0') {
          iVar2 = thunk_FUN_012aa7d6(&DAT_026bad30);
          if (iVar2 != 0) {
            DAT_026bad28 = FUN_000e4a10(s_networking_investment_server_obj_0163c8b4);
            thunk_FUN_012aa7e6(&DAT_026bad30);
          }
        }
        uVar4 = FUN_000e9fa0(param_2);
        FUN_01008290(local_168,s_networking_investment_server_obj_0163c8b4,uVar4,*param_3);
        FUN_000e4aa0(DAT_026bad28,local_168);
      }
LAB_0056cbf7:
      if (*DAT_01a1f100 == local_28) {
        return param_1;
      }
      lVar3 = thunk_FUN_012aa7f6();
      return lVar3;
    }
  }
  param_1 = param_1 + lVar3;
  goto LAB_0056cbf7;
}

