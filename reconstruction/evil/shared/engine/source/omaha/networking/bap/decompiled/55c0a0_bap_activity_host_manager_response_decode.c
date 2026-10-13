
undefined1
FUN_0055c0a0(undefined8 param_1,byte *param_2,int param_3,uint param_4,undefined4 *param_5,
            byte *param_6)

{
  byte bVar1;
  char cVar2;
  undefined1 uVar3;
  int iVar4;
  undefined4 uVar5;
  undefined1 local_1b8 [64];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (param_3 == 0x89) {
    if (0x88 < param_4) {
      bVar1 = *param_2;
      *param_6 = bVar1;
      if (bVar1 == 2) {
        thunk_FUN_012aa7c6(param_6 + 1,param_2 + 1,0x88);
        FUN_002a3620(param_6 + 1);
        uVar3 = 1;
      }
      else {
        cVar2 = FUN_000e4d70(7,4);
        uVar3 = 0;
        if (cVar2 != '\0') {
          if (DAT_026ba4a8 == '\0') {
            iVar4 = thunk_FUN_012aa7d6(&DAT_026ba4a8);
            if (iVar4 != 0) {
              DAT_026ba4a0 = FUN_000e4a10(s_networking_investment_bap_client_0163971b);
              thunk_FUN_012aa7e6(&DAT_026ba4a8);
            }
          }
          local_1b8[0] = 0;
          if (*param_6 < 6) {
            FUN_0100a3d0(local_1b8,&DAT_0160ec9c);
          }
          else {
            FUN_00065030(local_1b8,s_enum_out_of_range_01639778,0x40);
          }
          uVar3 = 0;
          FUN_01008290(local_178,s_networking_investment_bap_client_0163971b,local_1b8);
          FUN_000e4aa0(DAT_026ba4a0,local_178);
        }
      }
      *param_5 = 0x89;
      goto LAB_0055c2d5;
    }
    cVar2 = FUN_000e4d70(7,4);
    uVar3 = 0;
    if (cVar2 == '\0') goto LAB_0055c2d5;
    if (DAT_026ba498 == '\0') {
      iVar4 = thunk_FUN_012aa7d6(&DAT_026ba498);
      if (iVar4 != 0) {
        DAT_026ba490 = FUN_000e4a10(s_networking_investment_bap_client_016396a8);
        thunk_FUN_012aa7e6(&DAT_026ba498);
      }
    }
    FUN_01008290(local_178,s_networking_investment_bap_client_016396a8,param_4,0x89);
    uVar5 = DAT_026ba490;
  }
  else {
    cVar2 = FUN_000e4d70(7,4);
    uVar3 = 0;
    if (cVar2 == '\0') goto LAB_0055c2d5;
    if (DAT_026ba488 == '\0') {
      iVar4 = thunk_FUN_012aa7d6(&DAT_026ba488);
      if (iVar4 != 0) {
        DAT_026ba480 = FUN_000e4a10(s_networking_investment_bap_client_01639635);
        thunk_FUN_012aa7e6(&DAT_026ba488);
      }
    }
    FUN_01008290(local_178,s_networking_investment_bap_client_01639635,param_3,0x89);
    uVar5 = DAT_026ba480;
  }
  uVar3 = 0;
  FUN_000e4aa0(uVar5,local_178);
LAB_0055c2d5:
  if (*DAT_01a1f100 == local_38) {
    return uVar3;
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

