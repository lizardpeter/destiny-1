
undefined8 FUN_005662d0(long param_1,undefined8 param_2)

{
  char cVar1;
  int iVar2;
  undefined8 uVar3;
  long lVar4;
  undefined1 uVar5;
  undefined4 uVar6;
  undefined8 local_2b80;
  undefined4 local_2b78;
  undefined8 local_2b74;
  int local_2b6c;
  undefined1 local_2b68;
  int local_2b67;
  int local_2b60;
  undefined1 local_2b5c [12];
  int aiStack_2b50 [2678];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_000730b0(param_1,&local_2b78,0xa8);
  uVar6 = local_2b78;
  if (local_2b6c == -1) {
    cVar1 = FUN_000e4d70(7,4);
    uVar5 = 0;
    if (cVar1 == '\0') goto LAB_00566700;
    if ((DAT_026baa38 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_026baa38), iVar2 != 0)) {
      DAT_026baa30 = FUN_000e4a10(s_networking_investment_push_queue_0163b5e5);
      thunk_FUN_012aa7e6(&DAT_026baa38);
    }
    uVar3 = FUN_000e9fa0(local_2b78);
    FUN_01008290(local_178,s_networking_investment_push_queue_0163b5e5,uVar3,local_2b74,local_2b6c,
                 local_2b68,local_2b67);
    uVar5 = 0;
    uVar6 = DAT_026baa30;
  }
  else {
    local_2b80 = local_2b74;
    local_2b60 = 0;
    lVar4 = (long)*(int *)(param_1 + 0x40) * 0x20;
    *(undefined8 *)(param_1 + 0x60 + lVar4) = *(undefined8 *)(param_1 + 0x38);
    *(undefined8 *)(param_1 + 0x58 + lVar4) = *(undefined8 *)(param_1 + 0x30);
    uVar3 = *(undefined8 *)(param_1 + 0x20);
    *(undefined8 *)(param_1 + 0x50 + lVar4) = *(undefined8 *)(param_1 + 0x28);
    *(undefined8 *)(param_1 + 0x48 + lVar4) = uVar3;
    *(int *)(param_1 + 0x40) = *(int *)(param_1 + 0x40) + 1;
    if (0 < local_2b67) {
      local_2b60 = 0;
      iVar2 = local_2b67;
      do {
        lVar4 = (long)local_2b60;
        local_2b60 = local_2b60 + 1;
        FUN_000730b0(param_1,local_2b5c + lVar4 * 0x10,0x80);
        if (aiStack_2b50[lVar4 * 4] != 0) {
          FUN_000732b0(param_1,aiStack_2b50[lVar4 * 4] << 3);
        }
        iVar2 = iVar2 + -1;
      } while (iVar2 != 0);
    }
    cVar1 = FUN_00072210(param_1);
    FUN_00072350(param_1,1);
    if (cVar1 == '\0') {
      uVar3 = FUN_0056b260();
      cVar1 = FUN_0056c0f0(uVar3,uVar6,&local_2b80,local_2b6c,&local_2b68,local_2b5c,local_2b60,
                           param_2);
      if (cVar1 != '\0') {
        if (local_2b67 == 0) {
          cVar1 = FUN_000e4d70(7,4);
          if (cVar1 != '\0') {
            if ((DAT_026baa68 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_026baa68), iVar2 != 0)) {
              DAT_026baa60 = FUN_000e4a10(s_networking_investment_push_queue_0163b7cc);
              thunk_FUN_012aa7e6(&DAT_026baa68);
            }
            uVar3 = FUN_000e9fa0(local_2b78);
            FUN_01008290(local_178,s_networking_investment_push_queue_0163b7cc,uVar3,local_2b74,
                         local_2b6c,local_2b68,local_2b67);
            FUN_000e4aa0(DAT_026baa60,local_178);
          }
        }
        else {
          FUN_00566740(param_1,uVar6,&local_2b80);
        }
        uVar3 = FUN_0056b260();
        FUN_0056c770(uVar3,uVar6,&local_2b80,local_2b6c,local_2b67,param_2);
        uVar5 = 1;
        goto LAB_00566700;
      }
      cVar1 = FUN_000e4d70(7,4);
      uVar5 = 1;
      if (cVar1 == '\0') goto LAB_00566700;
      if ((DAT_026baa58 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_026baa58), iVar2 != 0)) {
        DAT_026baa50 = FUN_000e4a10(s_networking_investment_push_queue_0163b734);
        thunk_FUN_012aa7e6(&DAT_026baa58);
      }
      uVar3 = FUN_000e9fa0(local_2b78);
      FUN_01008290(local_178,s_networking_investment_push_queue_0163b734,uVar3,local_2b74,local_2b6c
                   ,local_2b68,local_2b67);
      uVar5 = 1;
      uVar6 = DAT_026baa50;
    }
    else {
      cVar1 = FUN_000e4d70(7,4);
      uVar5 = 0;
      if (cVar1 == '\0') goto LAB_00566700;
      if ((DAT_026baa48 == '\0') && (iVar2 = thunk_FUN_012aa7d6(&DAT_026baa48), iVar2 != 0)) {
        DAT_026baa40 = FUN_000e4a10(s_networking_investment_push_queue_0163b68e);
        thunk_FUN_012aa7e6(&DAT_026baa48);
      }
      uVar3 = FUN_000e9fa0(local_2b78);
      FUN_01008290(local_178,s_networking_investment_push_queue_0163b68e,uVar3,local_2b74,local_2b6c
                   ,local_2b68,local_2b67);
      uVar5 = 0;
      uVar6 = DAT_026baa40;
    }
  }
  FUN_000e4aa0(uVar6,local_178);
LAB_00566700:
  if (*DAT_01a1f100 != local_38) {
    uVar3 = thunk_FUN_012aa7f6();
    return uVar3;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar5);
}

