
undefined8 FUN_00792cd0(long param_1)

{
  char cVar1;
  int iVar2;
  ulong uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  ulong uVar6;
  undefined1 uVar7;
  int local_280;
  int local_27c;
  undefined1 local_278 [320];
  undefined1 local_138 [256];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar3 = *(ulong *)(param_1 + 8);
  uVar6 = 0;
  uVar7 = 0;
  do {
    if ((uVar3 >> (uVar6 & 0x3f) & 1) != 0) {
      local_27c = -1;
      local_138[0] = 0;
      iVar2 = FUN_00792ed0(param_1,uVar6 & 0xffffffff,local_138,&local_27c);
      if (iVar2 == 1) goto LAB_00792ea5;
      if (iVar2 != 0) {
        if ((DAT_026cf950 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_026cf950), iVar2 != 0)) {
          DAT_026cf94c = FUN_000e4a10(s__world_controller_state_manager__0165995f + 1);
          thunk_FUN_012aa7e6(&DAT_026cf950);
        }
        uVar5 = FUN_000e9fa0(uVar6 & 0xffffffff);
        uVar4 = FUN_00783960(local_27c);
        FUN_01008290(local_278,s__world_controller_state_manager__0165995f + 1,uVar5,uVar4);
        FUN_000e4aa0(DAT_026cf94c,local_278);
        local_280 = -1;
        cVar1 = FUN_007926b0(param_1,&local_280);
        iVar2 = local_27c;
        if ((cVar1 != '\0') && (iVar2 = local_280, local_280 != local_27c)) {
          if ((DAT_026cf960 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_026cf960), iVar2 != 0)) {
            DAT_026cf958 = FUN_000e4a10(s_world_controller_state_manager__B_016599c7);
            thunk_FUN_012aa7e6(&DAT_026cf960);
          }
          iVar2 = local_280;
          uVar5 = FUN_00783960(local_280);
          FUN_01008290(local_278,s_world_controller_state_manager__B_016599c7,uVar5);
          FUN_000e4aa0(DAT_026cf958,local_278);
          local_27c = iVar2;
        }
        FUN_00783ee0(0x19,iVar2,local_138);
        uVar7 = 0;
        goto LAB_00792ea5;
      }
      uVar3 = *(ulong *)(param_1 + 8);
    }
    uVar6 = uVar6 + 1;
    if (0x25 < (int)uVar6) {
      uVar7 = 1;
      if ((uVar3 & 0x40000000) != 0) {
        FUN_007933d0(param_1);
      }
LAB_00792ea5:
      if (*DAT_01a1f100 != local_38) {
        uVar5 = thunk_FUN_012aa7f6();
        return uVar5;
      }
      return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar7);
    }
  } while( true );
}

