
undefined8 FUN_0076af00(undefined8 param_1,undefined4 param_2,undefined4 param_3)

{
  undefined1 auVar1 [16];
  char cVar2;
  int iVar3;
  float fVar4;
  float fVar5;
  undefined8 uVar6;
  undefined1 local_168 [320];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  fVar4 = (float)FUN_00768480(param_2);
  fVar5 = (float)FUN_00768710(param_3);
  cVar2 = FUN_000e4d70(6,1);
  if (cVar2 != '\0') {
    if (DAT_026ca200 == '\0') {
      iVar3 = thunk_FUN_012aa7d6(&DAT_026ca200);
      if (iVar3 != 0) {
        DAT_026ca1f8 = FUN_000e4a10(s_world_controller_matchmaking_man_0164d044);
        thunk_FUN_012aa7e6(&DAT_026ca200);
      }
    }
    FUN_01008290((double)(fVar4 * fVar5),(double)fVar4,(double)fVar5,local_168,
                 s_world_controller_matchmaking_man_0164d044,param_2,param_3);
    FUN_000e4aa0(DAT_026ca1f8,local_168);
  }
  auVar1 = vmaxss_avx(ZEXT416((uint)(fVar4 * fVar5)),ZEXT816(0) << 0x40);
  auVar1 = vminss_avx(auVar1,ZEXT416(DAT_0164cdd4));
  if (*DAT_01a1f100 == local_28) {
    return auVar1._0_8_;
  }
  uVar6 = thunk_FUN_012aa7f6();
  return uVar6;
}

