
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0075f210(long *param_1,long *param_2)

{
  char cVar1;
  int iVar2;
  long lVar3;
  long *plVar4;
  undefined8 uVar5;
  undefined1 uVar6;
  undefined1 local_180 [16];
  undefined1 local_170 [320];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  lVar3 = FUN_0075d330();
  if (lVar3 != 0) {
    cVar1 = FUN_002999b0(lVar3);
    if (cVar1 != '\0') {
      lVar3 = FUN_0029c3b0(lVar3);
      FUN_002a3cc0(local_180,lVar3 + 8);
      do {
        cVar1 = FUN_002a3cd0(local_180);
        if (cVar1 == '\0') goto LAB_0075f2b0;
        plVar4 = (long *)FUN_002a3d50(local_180);
      } while (*param_1 != *plVar4);
      lVar3 = FUN_002a3d30(local_180);
      lVar3 = *(long *)(lVar3 + 0xa0);
      *param_2 = lVar3;
      uVar6 = 1;
      if (lVar3 != -1) goto LAB_0075f36a;
    }
  }
LAB_0075f2b0:
  cVar1 = FUN_00752150(0);
  if (cVar1 == '\0') {
    iVar2 = FUN_000697a0();
    uVar6 = 0;
    if (30000 < (uint)(iVar2 - _DAT_026c9918)) {
      cVar1 = FUN_000e4d70(3,3);
      if (cVar1 != '\0') {
        if (DAT_026c9920 == '\0') {
          iVar2 = thunk_FUN_012aa7d6(&DAT_026c9920);
          if (iVar2 != 0) {
            DAT_026c991c = FUN_000e4a10(s_world_controller__Function_firet_0164af06);
            thunk_FUN_012aa7e6(&DAT_026c9920);
          }
        }
        uVar5 = FUN_002487e0(param_1);
        FUN_01008290(local_170,s_world_controller__Function_firet_0164af06,uVar5);
        FUN_000e4aa0(DAT_026c991c,local_170);
      }
      _DAT_026c9918 = FUN_000697a0();
    }
  }
  else {
    *param_2 = 0;
    uVar6 = 1;
  }
LAB_0075f36a:
  if (*DAT_01a1f100 == local_30) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar6);
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

