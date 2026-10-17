
undefined8 FUN_0055b620(void)

{
  char cVar1;
  undefined1 uVar2;
  byte bVar3;
  byte bVar4;
  short sVar5;
  int iVar6;
  int iVar7;
  long lVar8;
  undefined8 uVar9;
  int in_ECX;
  undefined4 uVar10;
  int *in_R8;
  long in_R9;
  int *piVar11;
  undefined1 local_250 [20];
  undefined4 local_23c;
  undefined8 local_230;
  undefined8 local_228;
  undefined8 local_220;
  undefined8 local_218;
  int local_210;
  undefined8 auStack_208 [17];
  undefined1 local_180;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_23c = 1;
  FUN_00072240(local_250);
  local_180 = 0;
  FUN_00072400(local_250);
  lVar8 = (long)local_210;
  auStack_208[lVar8 * 4 + 3] = local_218;
  auStack_208[lVar8 * 4 + 2] = local_220;
  auStack_208[lVar8 * 4 + 1] = local_228;
  auStack_208[lVar8 * 4] = local_230;
  local_210 = local_210 + 1;
  *in_R8 = 0;
  if (in_ECX < 0x20) {
    cVar1 = FUN_000e4d70(8,4);
    bVar4 = 0;
    if (cVar1 == '\0') goto LAB_0055b904;
    if (DAT_026ba3d8 == '\0') {
      iVar6 = thunk_FUN_012aa7d6(&DAT_026ba3d8);
      if (iVar6 != 0) {
        DAT_026ba3d0 = FUN_000e4a10(s_networking_investment_account_id_01639215);
        thunk_FUN_012aa7e6(&DAT_026ba3d8);
      }
    }
    FUN_01008290(local_178,s_networking_investment_account_id_01639215);
    uVar10 = DAT_026ba3d0;
  }
  else {
    sVar5 = FUN_00072c70(local_250,0x10);
    iVar6 = FUN_00072c70(local_250,8);
    iVar7 = FUN_00072c70(local_250,8);
    cVar1 = FUN_00072210(local_250);
    if (cVar1 == '\0') {
      bVar4 = 0;
      if (((iVar6 != 7) && (iVar6 != 0xff)) || ((iVar7 != 7 && (iVar7 != 0xff)))) goto LAB_0055b904;
      piVar11 = (int *)(*in_R8 + in_R9);
      piVar11[6] = 0;
      piVar11[7] = 0;
      piVar11[4] = 0;
      piVar11[5] = 0;
      piVar11[2] = 0;
      piVar11[3] = 0;
      piVar11[0] = 0;
      piVar11[1] = 0;
      *in_R8 = *in_R8 + 0x20;
      *piVar11 = iVar6;
      piVar11[1] = iVar7;
      *(short *)(piVar11 + 2) = sVar5;
      if (sVar5 * 8 + sVar5 * 0x30 + *in_R8 <= in_ECX) {
        bVar3 = FUN_0055b9a0(*piVar11,local_250,piVar11,in_R8,in_R9);
        bVar4 = FUN_0055b9a0(piVar11[1],local_250,piVar11,in_R8,in_R9);
        bVar4 = bVar4 & bVar3;
        goto LAB_0055b904;
      }
      cVar1 = FUN_000e4d70(8,4);
      if (cVar1 == '\0') goto LAB_0055b904;
      if (DAT_026ba3e8 == '\0') {
        iVar6 = thunk_FUN_012aa7d6(&DAT_026ba3e8);
        if (iVar6 != 0) {
          DAT_026ba3e0 = FUN_000e4a10(s_networking_investment_account_id_01639290);
          thunk_FUN_012aa7e6(&DAT_026ba3e8);
        }
      }
      FUN_01008290(local_178,s_networking_investment_account_id_01639290);
      uVar10 = DAT_026ba3e0;
    }
    else {
      cVar1 = FUN_000e4d70(8,4);
      bVar4 = 0;
      if (cVar1 == '\0') goto LAB_0055b904;
      if (DAT_026ba408 == '\0') {
        iVar6 = thunk_FUN_012aa7d6(&DAT_026ba408);
        if (iVar6 != 0) {
          DAT_026ba400 = FUN_000e4a10(s_networking_investment_account_id_0163936a);
          thunk_FUN_012aa7e6(&DAT_026ba408);
        }
      }
      FUN_01008290(local_178,s_networking_investment_account_id_0163936a);
      uVar10 = DAT_026ba400;
    }
  }
  bVar4 = 0;
  FUN_000e4aa0(uVar10,local_178);
LAB_0055b904:
  uVar2 = FUN_00072210(local_250);
  FUN_00072350(local_250,uVar2);
  FUN_00072650(local_250);
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),bVar4);
  }
  uVar9 = thunk_FUN_012aa7f6();
  return uVar9;
}

