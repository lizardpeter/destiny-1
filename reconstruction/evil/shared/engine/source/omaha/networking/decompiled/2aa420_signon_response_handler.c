
bool FUN_002aa420(long param_1,undefined8 param_2,undefined8 param_3)

{
  char cVar1;
  char cVar2;
  undefined1 uVar3;
  int iVar4;
  uint uVar5;
  long lVar6;
  undefined8 uVar7;
  ulong uVar8;
  undefined4 uVar9;
  undefined1 local_968 [32];
  ulong local_948 [4];
  undefined4 local_928;
  uint uStack_924;
  undefined1 local_920 [640];
  char local_6a0;
  undefined1 local_698 [544];
  char local_478;
  undefined8 local_470;
  undefined4 local_468;
  code *local_460;
  long local_458;
  char local_450;
  undefined8 local_448;
  char local_440;
  undefined1 local_43f [64];
  char local_3ff;
  undefined1 local_3f8 [280];
  char local_2e0;
  uint uStack_2dc;
  char local_2d8;
  long local_2d0;
  undefined4 auStack_2c8 [64];
  char local_1c8;
  long local_1c0;
  undefined2 local_1b8;
  char local_177;
  uint local_174;
  undefined1 local_170 [320];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  cVar1 = FUN_000e4d70(0xd,0);
  if (cVar1 != '\0') {
    if ((DAT_0265af08 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_0265af08), iVar4 != 0)) {
      DAT_0265af00 = FUN_000e4a10(s_networking_signon_client__Parsin_016243ce);
      thunk_FUN_012aa7e6(&DAT_0265af08);
    }
    FUN_01008290(&local_928,s_networking_signon_client__Parsin_016243ce,param_3);
    FUN_000e4aa0(DAT_0265af00,&local_928);
  }
  local_460 = FUN_002aad90;
  local_458 = param_1;
  FUN_000a1470(local_968,param_2,param_3);
  FUN_000a2020(local_968,&DAT_01910cc0,&local_928);
  FUN_00240cd0();
  lVar6 = FUN_0034e3a0();
  FUN_0122bd50(*(undefined4 *)(lVar6 + 0x40));
  if ((((local_1c8 != '\0') && (0 < local_1c0)) &&
      (lVar6 = FUN_000696a0(), 4 < (ulong)((lVar6 + 2) - local_1c0))) &&
     (cVar1 = FUN_000e4d70(0xd,4), cVar1 != '\0')) {
    if ((DAT_0265af18 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_0265af18), iVar4 != 0)) {
      DAT_0265af10 = FUN_000e4a10(s_networking_signon_client__Client_01624412);
      thunk_FUN_012aa7e6(&DAT_0265af18);
    }
    FUN_01008290(local_170,s_networking_signon_client__Client_01624412,lVar6 - local_1c0);
    FUN_000e4aa0(DAT_0265af10,local_170);
  }
  if (((char)local_1b8 != '\0') && (0xff < local_1b8)) {
    FUN_00065030(param_1 + 0x47d4,(long)&local_1b8 + 1,0x40);
    cVar1 = FUN_000e4d70(0xd,4);
    if (cVar1 != '\0') {
      if ((DAT_0265af28 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_0265af28), iVar4 != 0)) {
        DAT_0265af20 = FUN_000e4a10(s_networking_signon_client__Server_01624462);
        thunk_FUN_012aa7e6(&DAT_0265af28);
      }
      FUN_01008290(local_170,s_networking_signon_client__Server_01624462,(long)&local_1b8 + 1);
      FUN_000e4aa0(DAT_0265af20,local_170);
    }
    if ((DAT_0265af38 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_0265af38), iVar4 != 0)) {
      DAT_0265af30 = FUN_00241890(s_environment_string_01624493);
      thunk_FUN_012aa7e6(&DAT_0265af38);
    }
    FUN_00241a20(DAT_0265af30,param_1 + 0x47d4,1);
  }
  local_948[0] = 0;
  local_948[1] = 0;
  local_948[2] = 0;
  if (local_177 != '\0') {
    local_948[0] = (ulong)local_174;
    local_948[2] = 0x40000;
  }
  uVar7 = FUN_002dfef0();
  FUN_002e03f0(uVar7,local_948);
  switch(local_928) {
  case 0:
    cVar2 = '\0';
    if ((uStack_924 & 0xff) != 0) {
      cVar2 = FUN_002aada0(param_1,local_920);
      thunk_FUN_012aa986(param_1 + 0x4580,0,0x104);
      if (((local_2d8 != '\0') && (local_2d0 != 0)) &&
         (*(int *)(param_1 + 0x4680) = (int)local_2d0, (int)local_2d0 != 0)) {
        uVar5 = 0;
        do {
          *(undefined4 *)(param_1 + 0x4580 + (ulong)uVar5 * 4) = auStack_2c8[uVar5];
          uVar5 = uVar5 + 1;
        } while (uVar5 < *(uint *)(param_1 + 0x4680));
      }
    }
    if (local_2e0 == '\0') {
      *(undefined1 *)(param_1 + 0x4579) = 0;
      *(undefined1 *)(param_1 + 0x457a) = 0;
      *(undefined4 *)(param_1 + 0x4474) = 0;
    }
    else {
      *(byte *)(param_1 + 0x4476) = (byte)(uStack_2dc >> 4) & 1;
      *(byte *)(param_1 + 0x4477) = (byte)(uStack_2dc >> 3) & 1;
      *(byte *)(param_1 + 0x4474) = (byte)(uStack_2dc >> 2) & 1;
      *(byte *)(param_1 + 0x457b) = (byte)(uStack_2dc >> 5) & 1;
      *(undefined1 *)(param_1 + 0x4475) = 0;
      *(undefined1 *)(param_1 + 0x4478) = 0;
      *(byte *)(param_1 + 0x4579) = (byte)(uStack_2dc >> 6) & 1;
      *(undefined1 *)(param_1 + 0x457a) = 0;
      *(undefined1 *)(param_1 + 0x457c) = 0;
    }
    break;
  case 1:
    cVar2 = '\0';
    if (local_6a0 != '\0') {
      FUN_002ab100(param_1,local_698);
      thunk_FUN_012aa986(param_1 + 0x4580,0,0x104);
      cVar2 = '\x01';
      if (((local_2d8 != '\0') && (local_2d0 != 0)) &&
         (*(int *)(param_1 + 0x4680) = (int)local_2d0, (int)local_2d0 != 0)) {
        uVar5 = 0;
        do {
          *(undefined4 *)(param_1 + 0x4580 + (ulong)uVar5 * 4) = auStack_2c8[uVar5];
          uVar5 = uVar5 + 1;
        } while (uVar5 < *(uint *)(param_1 + 0x4680));
      }
    }
    if (local_2e0 == '\0') {
      *(undefined4 *)(param_1 + 0x4474) = 0;
      *(undefined4 *)(param_1 + 0x4579) = 0;
    }
    else {
      *(byte *)(param_1 + 0x4476) = (byte)(uStack_2dc >> 4) & 1;
      *(byte *)(param_1 + 0x4477) = (byte)(uStack_2dc >> 3) & 1;
      *(byte *)(param_1 + 0x4474) = (byte)(uStack_2dc >> 2) & 1;
      *(undefined1 *)(param_1 + 0x4475) = 0;
      *(undefined1 *)(param_1 + 0x4478) = 0;
      *(byte *)(param_1 + 0x4579) = (byte)(uStack_2dc >> 6) & 1;
      *(undefined1 *)(param_1 + 0x457a) = 0;
    }
    break;
  case 2:
    cVar2 = '\0';
    if (local_3ff != '\0') {
      FUN_002ab340(param_1,local_3f8);
      cVar2 = '\x01';
    }
    break;
  case 3:
    *(undefined4 *)(param_1 + 0x4040) = 10;
    *(undefined1 *)(param_1 + 0x424d) = 0;
    cVar1 = FUN_000e4d70(0xd,2);
    if (cVar1 != '\0') {
      if ((DAT_0295c080 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_0295c080), iVar4 != 0)) {
        DAT_0295c078 = FUN_000e4a10(s_networking_signon_client__Signon_01624bdc);
        thunk_FUN_012aa7e6(&DAT_0295c080);
      }
      FUN_01008290(local_170,s_networking_signon_client__Signon_01624bdc,
                   (&PTR_s__none_01911110)[*(uint *)(param_1 + 0x4040)]);
      FUN_000e4aa0(DAT_0295c078,local_170);
    }
    *(byte *)(param_1 + 0x4474) = (byte)uStack_2dc >> 2 & 1;
    *(undefined1 *)(param_1 + 0x4475) = 0;
    *(byte *)(param_1 + 0x457b) = (byte)uStack_2dc >> 5 & 1;
    *(undefined1 *)(param_1 + 0x457c) = 0;
    cVar2 = '\x01';
    *(byte *)(param_1 + 0x4579) = (byte)uStack_2dc >> 6 & 1;
    *(undefined1 *)(param_1 + 0x457a) = 0;
    break;
  default:
    cVar1 = FUN_000e4d70(0xd,4);
    cVar2 = '\0';
    if (cVar1 != '\0') {
      if ((DAT_0265af48 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_0265af48), iVar4 != 0)) {
        DAT_0265af40 = FUN_000e4a10(s_networking_signon_client__Unknow_016244a6);
        thunk_FUN_012aa7e6(&DAT_0265af48);
      }
      cVar2 = '\0';
      FUN_01008290(local_170,s_networking_signon_client__Unknow_016244a6,local_928);
      FUN_000e4aa0(DAT_0265af40,local_170);
    }
  }
  if (local_450 == '\0') {
    *(undefined8 *)(param_1 + 0x41f8) = 0;
    cVar1 = FUN_000e4d70(0xd,4);
    if (cVar1 == '\0') goto LAB_002aabc0;
    if ((DAT_0265af68 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_0265af68), iVar4 != 0)) {
      DAT_0265af60 = FUN_000e4a10(s_networking_signon_client__Signon_01624530);
      thunk_FUN_012aa7e6(&DAT_0265af68);
    }
    FUN_01008290(local_170,s_networking_signon_client__Signon_01624530);
    uVar9 = DAT_0265af60;
  }
  else {
    *(undefined8 *)(param_1 + 0x41f8) = local_448;
    uVar8 = FUN_002406a0();
    *(ulong *)(param_1 + 0x41f8) = *(ulong *)(param_1 + 0x41f8) | uVar8;
    cVar1 = FUN_000e4d70(0xd,3);
    if (cVar1 == '\0') goto LAB_002aabc0;
    if ((DAT_0265af58 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_0265af58), iVar4 != 0)) {
      DAT_0265af50 = FUN_000e4a10(s_networking_signon_client__Silo_I_016244e8);
      thunk_FUN_012aa7e6(&DAT_0265af58);
    }
    FUN_01008290(local_170,s_networking_signon_client__Silo_I_016244e8,
                 *(undefined8 *)(param_1 + 0x41f8));
    uVar9 = DAT_0265af50;
  }
  FUN_000e4aa0(uVar9,local_170);
LAB_002aabc0:
  if (local_440 == '\0') {
    *(undefined1 *)(param_1 + 0x420c) = 0;
    cVar1 = FUN_000e4d70(0xd,4);
    if (cVar1 != '\0') {
      if ((DAT_0265af78 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_0265af78), iVar4 != 0)) {
        DAT_0265af70 = FUN_000e4a10(s_networking_signon_client__Signon_01624571);
        thunk_FUN_012aa7e6(&DAT_0265af78);
      }
      FUN_01008290(local_170,s_networking_signon_client__Signon_01624571);
      FUN_000e4aa0(DAT_0265af70,local_170);
    }
  }
  else {
    FUN_00065030((undefined1 *)(param_1 + 0x420c),local_43f,0x40);
  }
  if (local_478 != '\0') {
    *(undefined8 *)(param_1 + 0x4468) = local_470;
    *(undefined4 *)(param_1 + 0x4470) = local_468;
    cVar1 = FUN_000e4d70(0xd,3);
    if (cVar1 != '\0') {
      if ((DAT_0265af88 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_0265af88), iVar4 != 0)) {
        DAT_0265af80 = FUN_000e4a10(s_networking_signon_client__client_016245c0);
        thunk_FUN_012aa7e6(&DAT_0265af88);
      }
      FUN_01008290(local_170,s_networking_signon_client__client_016245c0,
                   *(undefined8 *)(param_1 + 0x4468),*(undefined4 *)(param_1 + 0x4470));
      FUN_000e4aa0(DAT_0265af80,local_170);
    }
  }
  if (cVar2 != '\0') {
    *(undefined8 *)(param_1 + 19000) = 0;
    *(undefined8 *)(param_1 + 0x4a30) = 0;
    *(undefined8 *)(param_1 + 0x4a28) = 0;
    *(undefined8 *)(param_1 + 0x4a20) = 0;
    *(undefined8 *)(param_1 + 0x4a18) = 0;
    *(undefined8 *)(param_1 + 0x4a10) = 0;
    *(undefined4 *)(param_1 + 0x4a1c) = 0xffffffff;
  }
  if (*DAT_01a1f100 != local_30) {
    uVar3 = thunk_FUN_012aa7f6();
    return (bool)uVar3;
  }
  return cVar2 != '\0';
}

