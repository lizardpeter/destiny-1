
undefined1
FUN_0055bd90(undefined8 param_1,byte *param_2,int param_3,uint param_4,undefined4 *param_5,
            byte *param_6)

{
  ushort *puVar1;
  byte bVar2;
  char cVar3;
  undefined1 uVar4;
  int iVar5;
  undefined4 uVar6;
  undefined1 local_1b8 [64];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (param_3 == 0x100f) {
    if (0x100e < param_4) {
      bVar2 = *param_2;
      *param_6 = bVar2;
      if (bVar2 == 3) {
        thunk_FUN_012aa7c6(param_6 + 1,param_2 + 1,0xe0c);
        puVar1 = (ushort *)(param_6 + 0x203);
        *puVar1 = *puVar1 << 8 | *puVar1 >> 8;
        puVar1 = (ushort *)(param_6 + 1);
        *puVar1 = *puVar1 << 8 | *puVar1 >> 8;
        uVar4 = 1;
      }
      else if (bVar2 == 1) {
        thunk_FUN_012aa7c6(param_6 + 1,param_2 + 1,0x100e);
        puVar1 = (ushort *)(param_6 + 0x405);
        *puVar1 = *puVar1 << 8 | *puVar1 >> 8;
        puVar1 = (ushort *)(param_6 + 1);
        *puVar1 = *puVar1 << 8 | *puVar1 >> 8;
        puVar1 = (ushort *)(param_6 + 0x203);
        *puVar1 = *puVar1 << 8 | *puVar1 >> 8;
        uVar4 = 1;
      }
      else {
        cVar3 = FUN_000e4d70(7,4);
        uVar4 = 0;
        if (cVar3 != '\0') {
          if (DAT_026ba478 == '\0') {
            iVar5 = thunk_FUN_012aa7d6(&DAT_026ba478);
            if (iVar5 != 0) {
              DAT_026ba470 = FUN_000e4a10(s_networking_investment_bap_activi_016395e3);
              thunk_FUN_012aa7e6(&DAT_026ba478);
            }
          }
          local_1b8[0] = 0;
          if (*param_6 < 6) {
            FUN_0100a3d0(local_1b8,&DAT_0160ec9c);
          }
          else {
            FUN_00065030(local_1b8,s_enum_out_of_range_01639778,0x40);
          }
          uVar4 = 0;
          FUN_01008290(local_178,s_networking_investment_bap_activi_016395e3,local_1b8);
          FUN_000e4aa0(DAT_026ba470,local_178);
        }
      }
      *param_5 = 0x100f;
      goto LAB_0055c001;
    }
    cVar3 = FUN_000e4d70(7,4);
    uVar4 = 0;
    if (cVar3 == '\0') goto LAB_0055c001;
    if (DAT_026ba468 == '\0') {
      iVar5 = thunk_FUN_012aa7d6(&DAT_026ba468);
      if (iVar5 != 0) {
        DAT_026ba460 = FUN_000e4a10(s_networking_investment_bap_activi_01639580);
        thunk_FUN_012aa7e6(&DAT_026ba468);
      }
    }
    FUN_01008290(local_178,s_networking_investment_bap_activi_01639580,param_4,0x100f);
    uVar6 = DAT_026ba460;
  }
  else {
    cVar3 = FUN_000e4d70(7,4);
    uVar4 = 0;
    if (cVar3 == '\0') goto LAB_0055c001;
    if (DAT_026ba458 == '\0') {
      iVar5 = thunk_FUN_012aa7d6(&DAT_026ba458);
      if (iVar5 != 0) {
        DAT_026ba450 = FUN_000e4a10(s_networking_investment_bap_activi_01639525);
        thunk_FUN_012aa7e6(&DAT_026ba458);
      }
    }
    FUN_01008290(local_178,s_networking_investment_bap_activi_01639525,param_3,0x100f);
    uVar6 = DAT_026ba450;
  }
  uVar4 = 0;
  FUN_000e4aa0(uVar6,local_178);
LAB_0055c001:
  if (*DAT_01a1f100 == local_38) {
    return uVar4;
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

