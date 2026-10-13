
undefined8
FUN_00567540(long param_1,undefined4 param_2,undefined8 *param_3,undefined8 param_4,
            undefined4 param_5)

{
  char cVar1;
  undefined4 uVar2;
  int iVar3;
  long *plVar4;
  long *plVar5;
  undefined8 uVar6;
  long lVar7;
  undefined8 *puVar8;
  undefined1 uVar9;
  byte bVar10;
  undefined4 local_18c;
  undefined1 local_188 [8];
  undefined4 *local_180;
  undefined1 local_178 [320];
  long local_38;
  
  bVar10 = 0;
  local_38 = *DAT_01a1f100;
  plVar4 = (long *)FUN_00560590(param_2);
  uVar2 = (**(code **)(*plVar4 + 0x10))(plVar4);
  plVar5 = (long *)FUN_0055af60(uVar2);
  cVar1 = (**(code **)(**(long **)(param_1 + 0x81e0) + 0x18))();
  if (cVar1 == '\0') {
    cVar1 = FUN_000e4d70(7,4);
    if (cVar1 != '\0') {
      if (DAT_026baae8 == '\0') {
        iVar3 = thunk_FUN_012aa7d6(&DAT_026baae8);
        if (iVar3 != 0) {
          DAT_026baae4 = FUN_000e4a10(s_networking_investment_bap_messag_0163b925);
          thunk_FUN_012aa7e6(&DAT_026baae8);
        }
      }
      FUN_01008290(local_178,s_networking_investment_bap_messag_0163b925,param_1 + 8,param_2,param_5
                  );
      FUN_000e4aa0(DAT_026baae4,local_178);
    }
  }
  else {
    uVar2 = (**(code **)(*plVar5 + 8))(plVar5);
    FUN_0055d370(uVar2);
    FUN_000b54b0(local_188,0x20068,0x18,s_enqueue_message_0163b9bf);
    local_18c = 0;
    cVar1 = (**(code **)(*plVar5 + 0x10))(plVar5,param_5,param_4,local_180 + 4,0x1ff6a,&local_18c);
    if (cVar1 != '\0') {
      cVar1 = (**(code **)(*plVar4 + 0x18))(plVar4);
      uVar2 = (**(code **)(**(long **)(param_1 + 0x81e0) + 8))();
      if (cVar1 == '\0') {
        FUN_00567940(param_1);
      }
      else {
        *local_180 = uVar2;
        local_180[1] = *(undefined4 *)(param_1 + 0x94);
        local_180[2] = param_2;
        local_180[3] = local_18c;
        puVar8 = (undefined8 *)(local_180 + 0x8004);
        for (lVar7 = 0xb; lVar7 != 0; lVar7 = lVar7 + -1) {
          *puVar8 = *param_3;
          param_3 = param_3 + (ulong)bVar10 * -2 + 1;
          puVar8 = puVar8 + (ulong)bVar10 * -2 + 1;
        }
        cVar1 = FUN_00bad5d0(local_180);
        if (cVar1 == '\0') {
          if (DAT_026bab08 == '\0') {
            iVar3 = thunk_FUN_012aa7d6(&DAT_026bab08);
            if (iVar3 != 0) {
              DAT_026bab00 = FUN_000e4a10(s_networking_investment_bap_messag_0163ba43);
              thunk_FUN_012aa7e6(&DAT_026bab08);
            }
          }
          FUN_01008290(local_178,s_networking_investment_bap_messag_0163ba43,param_1 + 8,param_2,
                       param_5);
          uVar2 = DAT_026bab00;
          goto LAB_00567827;
        }
      }
      FUN_000b54e0(local_188);
      uVar9 = 1;
      goto LAB_00567900;
    }
    if (DAT_026baaf8 == '\0') {
      iVar3 = thunk_FUN_012aa7d6(&DAT_026baaf8);
      if (iVar3 != 0) {
        DAT_026baaf0 = FUN_000e4a10(s_networking_investment_bap_messag_0163b9cf);
        thunk_FUN_012aa7e6(&DAT_026baaf8);
      }
    }
    FUN_01008290(local_178,s_networking_investment_bap_messag_0163b9cf,param_1 + 8,param_2,param_5);
    uVar2 = DAT_026baaf0;
LAB_00567827:
    FUN_000e4aa0(uVar2,local_178);
    FUN_000b54e0(local_188);
  }
  if (DAT_026bab18 == '\0') {
    iVar3 = thunk_FUN_012aa7d6(&DAT_026bab18);
    if (iVar3 != 0) {
      DAT_026bab10 = FUN_000e4a10(s_networking_investment_bap_messag_0163badb);
      thunk_FUN_012aa7e6(&DAT_026bab18);
    }
  }
  uVar9 = 0;
  FUN_01008290(local_178,s_networking_investment_bap_messag_0163badb,param_1 + 8,param_2,param_5);
  FUN_000e4aa0(DAT_026bab10,local_178);
  (**(code **)**(undefined8 **)(param_1 + 0x81e0))
            (*(undefined8 **)(param_1 + 0x81e0),1,*(undefined4 *)(param_1 + 0x94),0);
LAB_00567900:
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar9);
  }
  uVar6 = thunk_FUN_012aa7f6();
  return uVar6;
}

