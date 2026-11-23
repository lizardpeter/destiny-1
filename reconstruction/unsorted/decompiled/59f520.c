
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0059f520(void)

{
  char cVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined8 uVar6;
  uint uVar7;
  code *local_1b8;
  undefined8 uStack_1b0;
  undefined1 local_1a8;
  undefined1 local_1a0 [40];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  switch(DAT_026bd700) {
  case 0:
    if (DAT_026bd70a != '\0') {
      FUN_0059fae0();
    }
    break;
  case 1:
    uStack_1b0 = 0;
    local_1a8 = 0;
    local_1b8 = FUN_0059fc40;
    cVar1 = FUN_002a9080(&DAT_02655df8);
    cVar2 = FUN_000e4d70(0xd,0);
    if (cVar1 == '\0') {
      if (cVar2 != '\0') {
        if ((DAT_026bd710 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026bd710), iVar3 != 0)) {
          DAT_026bd70c = FUN_000e4a10(s_networking_online_ownership_mana_01640b41);
          thunk_FUN_012aa7e6(&DAT_026bd710);
        }
        FUN_01008290(local_178,s_networking_online_ownership_mana_01640b41,
                     (&PTR_DAT_019426c0)[DAT_026bd700]);
        FUN_000e4aa0(DAT_026bd70c,local_178);
      }
      cVar1 = FUN_002a8ba0(&DAT_02655df8,&local_1b8,0);
      if (cVar1 == '\0') {
        iVar3 = FUN_000697a0();
        if (30000 < (uint)(iVar3 - _DAT_026bd718)) {
          cVar1 = FUN_000e4d70(0xd,0);
          if (cVar1 != '\0') {
            if ((DAT_026bd720 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026bd720), iVar3 != 0)) {
              DAT_026bd71c = FUN_000e4a10(s_networking_online_ownership_mana_01640b76);
              thunk_FUN_012aa7e6(&DAT_026bd720);
            }
            FUN_01008290(local_178,s_networking_online_ownership_mana_01640b76);
            FUN_000e4aa0(DAT_026bd71c,local_178);
          }
          _DAT_026bd718 = FUN_000697a0();
        }
        break;
      }
    }
    else {
      if (cVar2 != '\0') {
        if ((DAT_026bd730 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026bd730), iVar3 != 0)) {
          DAT_026bd728 = FUN_000e4a10(s_networking_online_ownership_mana_01640be7);
          thunk_FUN_012aa7e6(&DAT_026bd730);
        }
        FUN_01008290(local_178,s_networking_online_ownership_mana_01640be7);
        FUN_000e4aa0(DAT_026bd728,local_178);
      }
      FUN_002a8710(&DAT_02655df8);
      FUN_002a8830(&DAT_02655df8,&local_1b8,0);
    }
    FUN_0059fd30(2);
    break;
  case 3:
    iVar3 = FUN_00559c30(0);
    if (iVar3 != 3) {
      cVar1 = FUN_000e4d70(0xd,3);
      if (cVar1 != '\0') {
        if ((DAT_026bd740 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026bd740), iVar4 != 0)) {
          DAT_026bd738 = FUN_000e4a10(s_networking_online_ownership_mana_01640c13);
          thunk_FUN_012aa7e6(&DAT_026bd740);
        }
        uVar6 = FUN_0055abb0(iVar3);
        FUN_01008290(local_178,s_networking_online_ownership_mana_01640c13,uVar6);
        FUN_000e4aa0(DAT_026bd738,local_178);
      }
      FUN_0059fd30(0);
      DAT_026bd708 = 0;
    }
    break;
  case 4:
    cVar1 = FUN_000b8fa0();
    if (cVar1 != '\0') {
      iVar3 = FUN_000b9080();
      if (iVar3 != 0) break;
      FUN_000b9350(4);
    }
    FUN_0059fd30(5);
    break;
  case 5:
    cVar1 = FUN_000b8fa0();
    if (cVar1 != '\0') {
      iVar3 = FUN_000b9080();
      if (iVar3 != 0) break;
      iVar3 = FUN_000b9710(4,local_1a0);
      uVar7 = 0;
      while (iVar3 != -1) {
        iVar4 = FUN_000b8170(iVar3);
        iVar3 = FUN_000b9880(local_1a0);
        if (1 < iVar4 + 0x1fffffffU) {
          (&DAT_026bd5f8)[uVar7] = iVar4;
          cVar1 = FUN_000e4d70(0xd,3);
          if (cVar1 != '\0') {
            if ((DAT_026bd750 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_026bd750), iVar5 != 0)) {
              DAT_026bd748 = FUN_000e4a10(s_networking_online_ownership_mana_01640c92);
              thunk_FUN_012aa7e6(&DAT_026bd750);
            }
            FUN_01008290(local_178,s_networking_online_ownership_mana_01640c92,iVar4);
            FUN_000e4aa0(DAT_026bd748,local_178);
          }
          uVar7 = uVar7 + 1;
        }
      }
      FUN_00244ee0(local_178);
      cVar1 = FUN_002457f0(local_178);
      cVar2 = FUN_00296830();
      if (cVar1 != '\0') {
        (&DAT_026bd5f8)[uVar7] = 0xe0000002;
        cVar1 = FUN_000e4d70(0xd,3);
        if (cVar1 != '\0') {
          if ((DAT_026bd760 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026bd760), iVar3 != 0)) {
            DAT_026bd758 = FUN_000e4a10(s_networking_online_ownership_mana_01640ce3);
            thunk_FUN_012aa7e6(&DAT_026bd760);
          }
          FUN_01008290(local_178,s_networking_online_ownership_mana_01640ce3,0xe0000002);
          FUN_000e4aa0(DAT_026bd758,local_178);
        }
        uVar7 = uVar7 + 1;
      }
      if (cVar2 == '\0') {
        (&DAT_026bd5f8)[uVar7] = 0xe0000001;
        cVar1 = FUN_000e4d70(0xd,3);
        if (cVar1 != '\0') {
          if ((DAT_026bd770 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_026bd770), iVar3 != 0)) {
            DAT_026bd768 = FUN_000e4a10(s_networking_online_ownership_mana_01640d40);
            thunk_FUN_012aa7e6(&DAT_026bd770);
          }
          FUN_01008290(local_178,s_networking_online_ownership_mana_01640d40,0xe0000001);
          FUN_000e4aa0(DAT_026bd768,local_178);
        }
        uVar7 = uVar7 + 1;
      }
      FUN_002f1790(cVar2);
      DAT_026bd6f8 = uVar7;
    }
    FUN_0059fe10();
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

