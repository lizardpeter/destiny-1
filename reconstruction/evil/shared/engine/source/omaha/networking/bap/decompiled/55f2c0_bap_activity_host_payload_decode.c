
undefined1 FUN_0055f2c0(byte *param_1,uint param_2,uint param_3,undefined4 *param_4,byte *param_5)

{
  byte bVar1;
  char cVar2;
  undefined1 uVar3;
  int iVar4;
  uint uVar5;
  undefined4 uVar6;
  undefined1 local_1b8 [64];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (param_2 < 0x1df12) {
    if (0x1df10 < param_3) {
      bVar1 = *param_1;
      *param_5 = bVar1;
      if (bVar1 == 1) {
        *(undefined8 *)(param_5 + 1) = *(undefined8 *)(param_1 + 1);
        FUN_002a3620(param_5 + 1);
        uVar6 = swap_bytes(*(undefined4 *)(param_1 + 9));
        *(undefined4 *)(param_5 + 9) = uVar6;
        uVar5 = *(uint *)(param_1 + 0xd);
        uVar6 = swap_bytes(uVar5);
        *(undefined4 *)(param_5 + 0xd) = uVar6;
        uVar5 = uVar5 >> 0x18 | (uVar5 & 0xff0000) >> 8 | (uVar5 & 0xff00) << 8 | uVar5 << 0x18;
        if (((int)uVar5 < 0) || (0x1df00 < uVar5)) {
          cVar2 = FUN_000e4d70(7,4);
          uVar3 = 0;
          if (cVar2 != '\0') {
            if (DAT_026ba660 == '\0') {
              iVar4 = thunk_FUN_012aa7d6(&DAT_026ba660);
              if (iVar4 != 0) {
                DAT_026ba658 = FUN_000e4a10(s_networking_investment_bap_client_0163a015);
                thunk_FUN_012aa7e6(&DAT_026ba660);
              }
            }
            FUN_01008290(local_178,s_networking_investment_bap_client_0163a015,
                         *(undefined4 *)(param_5 + 0xd));
            uVar6 = DAT_026ba658;
            goto LAB_0055f5aa;
          }
        }
        else {
          thunk_FUN_012aa7c6(param_5 + 0x11,param_1 + 0x11,(long)(int)uVar5);
          uVar3 = 1;
        }
      }
      else {
        cVar2 = FUN_000e4d70(7,4);
        uVar3 = 0;
        if (cVar2 != '\0') {
          if (DAT_026ba670 == '\0') {
            iVar4 = thunk_FUN_012aa7d6(&DAT_026ba670);
            if (iVar4 != 0) {
              DAT_026ba668 = FUN_000e4a10(s_networking_investment_bap_client_0163a06d);
              thunk_FUN_012aa7e6(&DAT_026ba670);
            }
          }
          local_1b8[0] = 0;
          if (*param_5 < 2) {
            FUN_0100a3d0(local_1b8,&DAT_0160ec9c);
          }
          else {
            FUN_00065030(local_1b8,s_enum_out_of_range_01639778,0x40);
          }
          FUN_01008290(local_178,s_networking_investment_bap_client_0163a06d,local_1b8);
          uVar6 = DAT_026ba668;
LAB_0055f5aa:
          uVar3 = 0;
          FUN_000e4aa0(uVar6,local_178);
        }
      }
      *param_4 = 0x1df11;
      goto LAB_0055f5bf;
    }
    cVar2 = FUN_000e4d70(7,4);
    uVar3 = 0;
    if (cVar2 == '\0') goto LAB_0055f5bf;
    if (DAT_026ba650 == '\0') {
      iVar4 = thunk_FUN_012aa7d6(&DAT_026ba650);
      if (iVar4 != 0) {
        DAT_026ba648 = FUN_000e4a10(s_networking_investment_bap_client_01639fb5);
        thunk_FUN_012aa7e6(&DAT_026ba650);
      }
    }
    FUN_01008290(local_178,s_networking_investment_bap_client_01639fb5,param_3,0x1df11);
    uVar6 = DAT_026ba648;
  }
  else {
    cVar2 = FUN_000e4d70(7,4);
    uVar3 = 0;
    if (cVar2 == '\0') goto LAB_0055f5bf;
    if (DAT_026ba640 == '\0') {
      iVar4 = thunk_FUN_012aa7d6(&DAT_026ba640);
      if (iVar4 != 0) {
        DAT_026ba638 = FUN_000e4a10(s_networking_investment_bap_client_01639f5d);
        thunk_FUN_012aa7e6(&DAT_026ba640);
      }
    }
    FUN_01008290(local_178,s_networking_investment_bap_client_01639f5d,param_2,0x1df11);
    uVar6 = DAT_026ba638;
  }
  uVar3 = 0;
  FUN_000e4aa0(uVar6,local_178);
LAB_0055f5bf:
  if (*DAT_01a1f100 == local_38) {
    return uVar3;
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

