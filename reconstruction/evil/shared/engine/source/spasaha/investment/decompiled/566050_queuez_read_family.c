
undefined1 FUN_00566050(undefined4 param_1,undefined8 param_2)

{
  long lVar1;
  char cVar2;
  undefined1 uVar3;
  undefined8 uVar4;
  long lVar5;
  uint uVar6;
  ushort uVar7;
  int iVar8;
  bool bVar9;
  int local_2d0 [2];
  undefined1 local_2c8 [136];
  undefined1 local_240 [320];
  undefined1 local_100 [20];
  undefined4 local_ec;
  undefined1 local_30;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  local_ec = 1;
  FUN_00072240(local_100,param_2,param_1);
  local_30 = 0;
  FUN_00072400(local_100);
  FUN_000730b0(local_100,local_2d0,0x20);
  if (local_2d0[0] == 0) {
    cVar2 = FUN_000e4d70(7,4);
    uVar3 = 0;
    if (cVar2 != '\0') {
      if ((DAT_026baa18 == '\0') && (iVar8 = thunk_FUN_012aa7d6(&DAT_026baa18), iVar8 != 0)) {
        DAT_026baa10 = FUN_000e4a10(s_networking_investment_push_queue_0163b555);
        thunk_FUN_012aa7e6(&DAT_026baa18);
      }
      uVar3 = 0;
      FUN_01008290(local_240,s_networking_investment_push_queue_0163b555,local_2d0[0]);
      FUN_000e4aa0(DAT_026baa10,local_240);
    }
  }
  else {
    lVar1 = *(long *)(PTR_DAT_019e4c18 + 8);
    iVar8 = -1;
    uVar4 = FUN_000e8680(lVar1,0,0xffffffff);
    thunk_FUN_012aa986(local_2c8,0,uVar4);
    uVar7 = *(ushort *)(lVar1 + 0x1c) & 0x78;
    bVar9 = uVar7 != 0;
    if (uVar7 == 0) {
      uVar6 = *(uint *)(lVar1 + 0x20);
      if ((*(ushort *)(lVar1 + 0x1c) & 0x40) != 0) {
        lVar5 = FUN_000e8a90(lVar1,local_2c8);
        if (lVar5 == 0) {
          uVar6 = uVar6 | 0x5488bf;
        }
        else {
          uVar6 = *(uint *)(lVar5 + 0x20) & 0x5488bf | uVar6;
        }
      }
      bVar9 = (uVar6 & 0xc08070) != 0;
    }
    if (bVar9) {
      iVar8 = -1;
      FUN_000e6730(lVar1,local_2c8,0,0xffffffff,0);
    }
    do {
      iVar8 = iVar8 + 1;
      uVar3 = 1;
      if (local_2d0[0] <= iVar8) break;
      cVar2 = FUN_005662d0(local_100,local_2c8);
      uVar3 = 0;
    } while (cVar2 != '\0');
  }
  FUN_00072650(local_100);
  cVar2 = FUN_00072210(local_100);
  if (cVar2 != '\0') {
    cVar2 = FUN_000e4d70(7,4);
    uVar3 = 0;
    if (cVar2 != '\0') {
      if ((DAT_026baa28 == '\0') && (iVar8 = thunk_FUN_012aa7d6(&DAT_026baa28), iVar8 != 0)) {
        DAT_026baa20 = FUN_000e4a10(s_networking_investment_push_queue_0163b59c);
        thunk_FUN_012aa7e6(&DAT_026baa28);
      }
      uVar3 = 0;
      FUN_01008290(local_240,s_networking_investment_push_queue_0163b59c);
      FUN_000e4aa0(DAT_026baa20,local_240);
    }
  }
  if (*DAT_01a1f100 != local_28) {
    uVar3 = thunk_FUN_012aa7f6();
    return uVar3;
  }
  return uVar3;
}

