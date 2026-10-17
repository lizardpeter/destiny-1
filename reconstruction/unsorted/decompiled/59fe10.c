
void FUN_0059fe10(void)

{
  char cVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  undefined8 local_310;
  undefined8 uStack_308;
  undefined8 local_300 [40];
  undefined1 local_1c0 [32];
  undefined1 local_1a0 [32];
  undefined1 local_180 [32];
  undefined1 local_160 [32];
  undefined1 local_140 [32];
  undefined1 local_120 [32];
  undefined1 local_100 [32];
  undefined1 local_e0 [32];
  undefined1 local_c0 [32];
  undefined8 *local_a0;
  undefined8 local_80;
  undefined8 uStack_78;
  undefined8 uStack_70;
  undefined8 uStack_68;
  undefined8 local_60;
  undefined8 uStack_58;
  undefined8 uStack_50;
  undefined8 uStack_48;
  undefined8 local_40;
  undefined8 local_38;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  if (DAT_026bd6fc != 2) {
    cVar1 = FUN_000e4d70(0xd,2);
    if (cVar1 != '\0') {
      if (DAT_026bd830 == '\0') {
        iVar3 = thunk_FUN_012aa7d6(&DAT_026bd830);
        if (iVar3 != 0) {
          DAT_026bd828 = FUN_000e4a10(s_networking_online_ownership_mana_0164115e);
          thunk_FUN_012aa7e6(&DAT_026bd830);
        }
      }
      FUN_01008290(local_300,s_networking_online_ownership_mana_0164115e);
      FUN_000e4aa0(DAT_026bd828,local_300);
    }
    FUN_0059fd30(0);
    DAT_026bd708 = 1;
    goto LAB_005a0292;
  }
  cVar1 = FUN_005876f0();
  if (cVar1 == '\0') {
    cVar1 = FUN_000e4d70(0xd,4);
    if (cVar1 != '\0') {
      if (DAT_026bd840 == '\0') {
        iVar3 = thunk_FUN_012aa7d6(&DAT_026bd840);
        if (iVar3 != 0) {
          DAT_026bd838 = FUN_000e4a10(s_networking_online_ownership_mana_016411bb);
          thunk_FUN_012aa7e6(&DAT_026bd840);
        }
      }
      FUN_01008290(local_300,s_networking_online_ownership_mana_016411bb);
      uVar4 = DAT_026bd838;
LAB_005a027c:
      FUN_000e4aa0(uVar4,local_300);
    }
  }
  else {
    local_60 = 0;
    uStack_58 = 0;
    uStack_50 = 0;
    uStack_48 = 0;
    local_80 = 0;
    uStack_78 = 0;
    uStack_70 = 0;
    uStack_68 = 0;
    local_38 = 0;
    local_40 = 0;
    FUN_001271d0(&uStack_68);
    local_310 = 0;
    uStack_308 = 0;
    local_1c0 = ZEXT432(0) << 0x40;
    local_a0 = (undefined8 *)0x0;
    local_1a0 = local_1c0;
    local_180 = local_1c0;
    local_160 = local_1c0;
    local_140 = local_1c0;
    local_120 = local_1c0;
    local_100 = local_1c0;
    local_e0 = local_1c0;
    local_c0 = local_1c0;
    if (DAT_02655cf0 == 5) {
      local_310 = DAT_02655d40;
      uStack_308 = DAT_02655d48;
      cVar1 = FUN_000e4d70(0xd,2);
      if (cVar1 != '\0') {
        if (DAT_026bd870 == '\0') {
          iVar3 = thunk_FUN_012aa7d6(&DAT_026bd870);
          if (iVar3 != 0) {
            DAT_026bd868 = FUN_000e4a10(s_networking_online_ownership_mana_016412d1);
            thunk_FUN_012aa7e6(&DAT_026bd870);
          }
        }
        FUN_01008290(local_300,s_networking_online_ownership_mana_016412d1);
        FUN_000e4aa0(DAT_026bd868,local_300);
      }
      local_1c0._0_16_ = ZEXT816(0);
      local_1c0._16_4_ = DAT_026bd6f8;
      local_1c0._20_4_ = 0;
      thunk_FUN_012aa7c6(local_1c0 + 0x18,&DAT_026bd5f8,0x100);
      local_c0._24_8_ = FUN_002ac090;
      local_a0 = &local_310;
      FUN_00072050(local_300,0xffffffff);
      cVar1 = FUN_0055aa80(0,0x17,&local_80,local_1c0,0x128,local_300[0]);
      if (cVar1 == '\0') {
        cVar2 = FUN_000e4d70(0xd,4);
        if (cVar2 != '\0') {
          if (DAT_026bd880 == '\0') {
            iVar3 = thunk_FUN_012aa7d6(&DAT_026bd880);
            if (iVar3 != 0) {
              DAT_026bd878 = FUN_000e4a10(s_networking_online_ownership_mana_01641317);
              thunk_FUN_012aa7e6(&DAT_026bd880);
            }
          }
          FUN_01008290(local_300,s_networking_online_ownership_mana_01641317);
          uVar4 = DAT_026bd878;
          goto LAB_005a01f3;
        }
      }
    }
    else {
      cVar2 = FUN_000e4d70(0xd,4);
      cVar1 = '\0';
      if (cVar2 != '\0') {
        if (DAT_026bd860 == '\0') {
          iVar3 = thunk_FUN_012aa7d6(&DAT_026bd860);
          if (iVar3 != 0) {
            DAT_026bd858 = FUN_000e4a10(s_networking_online_ownership_mana_01641289);
            thunk_FUN_012aa7e6(&DAT_026bd860);
          }
        }
        cVar1 = '\0';
        FUN_01008290(local_300,s_networking_online_ownership_mana_01641289);
        uVar4 = DAT_026bd858;
LAB_005a01f3:
        FUN_000e4aa0(uVar4,local_300);
      }
    }
    if (cVar1 != '\0') {
      FUN_0059fd30(3);
      FUN_0059deb0(1);
      goto LAB_005a0292;
    }
    cVar1 = FUN_000e4d70(0xd,4);
    if (cVar1 != '\0') {
      if (DAT_026bd850 == '\0') {
        iVar3 = thunk_FUN_012aa7d6(&DAT_026bd850);
        if (iVar3 != 0) {
          DAT_026bd848 = FUN_000e4a10(s_networking_online_ownership_mana_01641237);
          thunk_FUN_012aa7e6(&DAT_026bd850);
        }
      }
      FUN_01008290(local_300,s_networking_online_ownership_mana_01641237);
      uVar4 = DAT_026bd848;
      goto LAB_005a027c;
    }
  }
  FUN_0059fd30(0);
  DAT_026bd708 = 0;
LAB_005a0292:
  if (*DAT_01a1f100 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

