
void FUN_002b65a0(undefined4 param_1,int param_2,char param_3,char param_4,long param_5,
                 undefined8 param_6)

{
  char cVar1;
  char cVar2;
  int iVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 local_8d0;
  undefined8 local_8c8;
  undefined1 local_8c0 [48];
  undefined1 local_890 [320];
  undefined1 local_750 [64];
  undefined4 local_710;
  undefined1 local_70b;
  undefined1 local_6ca;
  undefined1 local_689;
  undefined1 local_648;
  undefined1 local_607;
  undefined1 local_5c6;
  undefined1 local_585;
  undefined1 local_544;
  undefined1 local_503;
  undefined1 local_4c2;
  undefined1 local_480 [64];
  undefined4 local_440;
  undefined1 local_43b;
  undefined1 local_3fa;
  undefined1 local_3b9;
  undefined1 local_378;
  undefined1 local_337;
  undefined1 local_2f6;
  undefined1 local_2b5;
  undefined1 local_274;
  undefined1 local_233;
  undefined1 local_1f2;
  undefined4 local_1b0;
  undefined1 local_190;
  undefined1 local_18f;
  undefined1 local_18e;
  undefined1 local_188 [24];
  undefined1 local_170 [48];
  undefined1 local_140 [8];
  undefined1 local_138 [256];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_00244ee0(local_140);
  FUN_002447a0(local_140,local_170);
  FUN_002b8460(local_170,local_188);
  if (param_2 == 2) {
    cVar2 = '\x01';
  }
  else {
    cVar2 = '\0';
    if (param_2 == 0) {
      cVar2 = param_4;
    }
    param_4 = cVar2;
    if (param_3 != '\0') {
      cVar1 = FUN_002e8b90(param_5);
      cVar2 = '\0';
      if (cVar1 == '\0') goto LAB_002b6667;
    }
    cVar2 = FUN_002e8c80(param_5);
  }
LAB_002b6667:
  if (param_4 == '\0') {
    DAT_0266ec40._4_4_ = 0;
    DAT_0266ec38 = param_6;
    DAT_0266ec40._0_4_ = param_1;
  }
  else if ((cVar2 == '\0') || (param_3 == '\0')) {
    if (cVar2 == '\0') {
      cVar2 = FUN_000e4d70(0x13,4);
      if (cVar2 != '\0') {
        if ((DAT_0266f090 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_0266f090), iVar3 != 0)) {
          DAT_0266f088 = FUN_000e4a10(s_networking_managed_session___msi_016257e7);
          thunk_FUN_012aa7e6(&DAT_0266f090);
        }
        uVar4 = FUN_002ea0f0(param_5);
        uVar5 = FUN_002e9f90(param_5 + 0x3c);
        FUN_01008290(local_890,s_networking_managed_session___msi_016257e7,param_1,uVar4,uVar5);
        FUN_000e4aa0(DAT_0266f088,local_890);
      }
      DAT_0266ec40._4_4_ = 0xffffffff;
      DAT_0266ec38 = param_6;
      DAT_0266ec40._0_4_ = param_1;
    }
    else {
      local_8c0[0] = 0;
      FUN_002e9a70(param_5 + 0x3c,local_8c0,0x2d);
      FUN_002bc910(&DAT_0266eda0,local_188);
      FUN_002bd2c0(&DAT_0266eda0,local_8c0);
      DAT_0266ec48 = 4;
      DAT_0266ec50 = &DAT_0266eda0;
      DAT_0266ec58 = param_6;
      DAT_0266ec60 = param_1;
      cVar2 = FUN_000e4d70(0x13,2);
      if (cVar2 != '\0') {
        if ((DAT_0266f080 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_0266f080), iVar3 != 0)) {
          DAT_0266f078 = FUN_000e4a10(s_networking_managed_session___msi_0162579d);
          thunk_FUN_012aa7e6(&DAT_0266f080);
        }
        uVar4 = FUN_002ea0f0(param_5);
        uVar5 = FUN_002e9f90(param_5 + 0x3c);
        FUN_01008290(local_890,s_networking_managed_session___msi_0162579d,param_1,uVar4,uVar5);
        FUN_000e4aa0(DAT_0266f078,local_890);
      }
    }
  }
  else {
    local_750[0] = 0;
    local_710 = 0;
    local_70b = 0;
    local_6ca = 0;
    local_689 = 0;
    local_648 = 0;
    local_607 = 0;
    local_5c6 = 0;
    local_585 = 0;
    local_544 = 0;
    local_503 = 0;
    local_4c2 = 0;
    local_480[0] = 0;
    local_440 = 0;
    local_43b = 0;
    local_3fa = 0;
    local_3b9 = 0;
    local_378 = 0;
    local_337 = 0;
    local_2f6 = 0;
    local_2b5 = 0;
    local_274 = 0;
    local_233 = 0;
    local_1f2 = 0;
    FUN_002bc830(&local_8c8,&local_8d0);
    thunk_FUN_012aa986(local_750,0,0x5c8);
    local_890[0] = 0;
    local_138[0] = 0;
    FUN_002f1e70(local_890,local_138);
    FUN_00065030(local_750,local_890,0x40);
    FUN_00065030(local_480,local_138,0x40);
    local_1b0 = 1;
    local_190 = 1;
    local_18f = 1;
    local_18e = 1;
    FUN_002bc910(&DAT_0266ec70,local_188);
    FUN_002bd350(&DAT_0266ec70,local_750,local_8c8,local_8d0,param_5,0x4e);
    DAT_0266ec48 = 1;
    DAT_0266ec50 = &DAT_0266ec70;
    DAT_0266ec58 = param_6;
    DAT_0266ec60 = param_1;
    DAT_0266ec68 = param_5;
    cVar2 = FUN_000e4d70(0x13,2);
    if (cVar2 != '\0') {
      if ((DAT_0266f070 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_0266f070), iVar3 != 0)) {
        DAT_0266f068 = FUN_000e4a10(s_networking_managed_session___msi_01625757);
        thunk_FUN_012aa7e6(&DAT_0266f070);
      }
      uVar4 = FUN_002ea0f0(param_5);
      FUN_01008290(local_890,s_networking_managed_session___msi_01625757,param_1,uVar4);
      FUN_000e4aa0(DAT_0266f068,local_890);
    }
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

