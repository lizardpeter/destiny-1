
undefined8
FUN_0055b220(undefined8 param_1,undefined8 param_2,uint *param_3,undefined8 param_4,
            undefined4 param_5,int *param_6)

{
  uint uVar1;
  uint uVar2;
  char cVar3;
  int iVar4;
  undefined8 uVar5;
  undefined8 *puVar6;
  long lVar7;
  undefined4 uVar8;
  undefined1 uVar9;
  undefined1 local_250 [20];
  undefined4 local_23c;
  int local_230;
  int local_22c;
  ulong local_228;
  int local_220;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_23c = 1;
  FUN_00072240(local_250,param_4,param_5);
  *param_6 = 0;
  FUN_000723b0(local_250,1);
  uVar1 = param_3[1];
  uVar2 = *param_3;
  if (0x40 - local_220 < 0x10) {
    FUN_000733a0(local_250,(ulong)(uint)(int)(short)param_3[2],0x10);
  }
  else {
    local_220 = local_220 + 0x10;
    local_22c = local_22c + 0x10;
    local_228 = local_228 << 0x10 | (ulong)(uint)(int)(short)param_3[2];
  }
  if (0x40 - local_220 < 8) {
    FUN_000733a0(local_250,(ulong)uVar2,8);
  }
  else {
    local_220 = local_220 + 8;
    local_22c = local_22c + 8;
    local_228 = local_228 << 8 | (ulong)uVar2;
  }
  if (0x40 - local_220 < 8) {
    FUN_000733a0(local_250,(ulong)uVar1,8);
  }
  else {
    local_220 = local_220 + 8;
    local_22c = local_22c + 8;
    local_228 = local_228 << 8 | (ulong)uVar1;
  }
  cVar3 = FUN_00072210(local_250);
  if (cVar3 == '\0') {
    uVar9 = 0;
    if (*param_3 == 0xff) {
      iVar4 = (int)(short)param_3[2];
      puVar6 = *(undefined8 **)(param_3 + 4);
      do {
        if (iVar4 == 0) goto LAB_0055b576;
        FUN_00073000(local_250,*puVar6,0x40);
        cVar3 = FUN_00072210(local_250);
        iVar4 = iVar4 + -1;
        puVar6 = puVar6 + 1;
      } while (cVar3 == '\0');
      cVar3 = FUN_000e4d70(8,4);
      if (cVar3 == '\0') goto LAB_0055b5b0;
      if (DAT_026ba428 == '\0') {
        iVar4 = thunk_FUN_012aa7d6(&DAT_026ba428);
        if (iVar4 != 0) {
          DAT_026ba420 = FUN_000e4a10(s_networking_investment_account_id_01639419);
          thunk_FUN_012aa7e6(&DAT_026ba428);
        }
      }
      FUN_01008290(local_178,s_networking_investment_account_id_01639419);
      uVar8 = DAT_026ba420;
    }
    else {
      if (*param_3 != 7) goto LAB_0055b5b0;
      iVar4 = (short)param_3[2] + 1;
      lVar7 = *(long *)(param_3 + 4);
      do {
        iVar4 = iVar4 + -1;
        if (iVar4 == 0) goto LAB_0055b576;
        cVar3 = FUN_002b8550(lVar7,local_250);
        lVar7 = lVar7 + 0x30;
      } while (cVar3 != '\0');
      cVar3 = FUN_000e4d70(8,4);
      if (cVar3 == '\0') goto LAB_0055b5b0;
      if (DAT_026ba418 == '\0') {
        iVar4 = thunk_FUN_012aa7d6(&DAT_026ba418);
        if (iVar4 != 0) {
          DAT_026ba410 = FUN_000e4a10(s_networking_investment_account_id_016393c4);
          thunk_FUN_012aa7e6(&DAT_026ba418);
        }
      }
      FUN_01008290(local_178,s_networking_investment_account_id_016393c4);
      uVar8 = DAT_026ba410;
    }
  }
  else {
    cVar3 = FUN_000e4d70(8,4);
    uVar9 = 0;
    if (cVar3 == '\0') goto LAB_0055b5b0;
    if (DAT_026ba3f8 == '\0') {
      iVar4 = thunk_FUN_012aa7d6(&DAT_026ba3f8);
      if (iVar4 != 0) {
        DAT_026ba3f0 = FUN_000e4a10(s_networking_investment_account_id_01639310);
        thunk_FUN_012aa7e6(&DAT_026ba3f8);
      }
    }
    FUN_01008290(local_178,s_networking_investment_account_id_01639310);
    uVar8 = DAT_026ba3f0;
  }
  uVar9 = 0;
  FUN_000e4aa0(uVar8,local_178);
LAB_0055b5b0:
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar9);
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
LAB_0055b576:
  FUN_00072560(local_250,0);
  uVar9 = 1;
  *param_6 = (int)(((uint)(local_230 + 7 + local_220 >> 0x1f) >> 0x1d) + 7 + local_230 + local_220)
             >> 3;
  goto LAB_0055b5b0;
}

