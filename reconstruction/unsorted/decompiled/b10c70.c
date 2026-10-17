
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00b10c70(undefined4 *param_1)

{
  uint uVar1;
  bool bVar2;
  bool bVar3;
  char cVar4;
  int iVar5;
  int iVar6;
  long *plVar7;
  long lVar8;
  undefined8 uVar9;
  long lVar10;
  long lVar11;
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  plVar7 = (long *)FUN_005979c0();
  lVar8 = (**(code **)(*plVar7 + 0x60))(plVar7,*param_1);
  uVar9 = FUN_00b0c560(*param_1);
  bVar3 = false;
  if ((long)(int)param_1[5] != -1) {
    if ((*(byte *)(param_1 + 1) & 8) == 0) {
      lVar10 = *(long *)(param_1 + 0x12);
      lVar11 = DAT_026553b0;
      if (DAT_026553a8 == '\0') {
        lVar11 = FUN_000694d0();
      }
      if (lVar11 - lVar10 <= DAT_027bd568) goto LAB_00b1117e;
    }
    else {
      lVar10 = *(long *)(param_1 + (long)(int)param_1[5] * 0x30 + 0x22);
      lVar11 = DAT_026553b0;
      if (DAT_026553a8 == '\0') {
        lVar11 = FUN_000694d0();
      }
      bVar3 = true;
      if (lVar11 - lVar10 <= DAT_027bd570) goto LAB_00b1117e;
    }
  }
  iVar5 = FUN_00b0c6d0(lVar8,uVar9);
  if (iVar5 == 0x12) {
    bVar2 = true;
    if (bVar3) {
      bVar3 = true;
    }
    else {
      bVar3 = false;
      if ((*(byte *)(param_1 + 1) & 0x80) != 0) {
        lVar10 = *(long *)(param_1 + (long)(int)param_1[5] * 0x30 + 0x1c);
        lVar11 = DAT_026553b0;
        if (DAT_026553a8 == '\0') {
          lVar11 = FUN_000694d0();
        }
        bVar2 = DAT_027bd578 <= lVar11 - lVar10;
        bVar3 = bVar2;
        if (lVar11 - lVar10 < DAT_027bd578) goto LAB_00b1117e;
      }
    }
    lVar10 = FUN_0034e3c0();
    if (-1 < *(int *)(lVar10 + 0xec)) {
      lVar11 = FUN_0034e3c0();
      lVar10 = *(long *)(param_1 + 0x16);
      if (lVar10 != -1) {
        iVar5 = *(int *)(lVar11 + 0xec);
        lVar11 = DAT_026553b0;
        if (DAT_026553a8 == '\0') {
          lVar11 = FUN_000694d0();
        }
        if (lVar11 - lVar10 < (long)iVar5) {
          iVar6 = FUN_000697a0();
          if (5000 < (uint)(iVar6 - _DAT_02802d30)) {
            cVar4 = FUN_000e4d70(6,2);
            if (cVar4 != '\0') {
              if ((DAT_02802d38 == '\0') && (iVar6 = thunk_FUN_012aa7d6(&DAT_02802d38), iVar6 != 0))
              {
                DAT_02802d34 = FUN_000e4a10(s_networking_logic_matchmaking_see_01685945);
                thunk_FUN_012aa7e6(&DAT_02802d38);
              }
              lVar8 = *(long *)(param_1 + 0x16);
              lVar10 = DAT_026553b0;
              if (DAT_026553a8 == '\0') {
                lVar10 = FUN_000694d0();
              }
              FUN_01008290(local_178,s_networking_logic_matchmaking_see_01685945,lVar10 - lVar8,
                           (long)iVar5);
              FUN_000e4aa0(DAT_02802d34,local_178);
            }
            _DAT_02802d30 = FUN_000697a0();
          }
          goto LAB_00b1117e;
        }
      }
      if (!bVar2) goto LAB_00b1117e;
    }
    lVar10 = thunk_FUN_00768060();
    if (*(char *)(param_1 + 0x18) != '\0') {
      param_1[6] = 0xffffffff;
      *(byte *)(param_1 + 1) = *(byte *)(param_1 + 1) & 0x7f;
      lVar11 = DAT_026553b0;
      if (DAT_026553a8 == '\0') {
        lVar11 = FUN_000694d0();
      }
      *(long *)(param_1 + 8) = lVar11;
      param_1[5] = 0xffffffff;
      *(undefined1 *)(param_1 + 0x18) = 0;
      bVar3 = false;
    }
    param_1[0xc] = param_1[0xc] + 1;
    lVar11 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      lVar11 = FUN_000694d0();
    }
    *(long *)(param_1 + 0x16) = lVar11;
    if (lVar10 != 0) {
      FUN_0076e170(lVar10,*param_1);
    }
    *(byte *)(param_1 + 1) = *(byte *)(param_1 + 1) & 0xf7;
    FUN_00b14190();
    param_1[0xe] = param_1[0xe] + param_1[0xd];
    param_1[0xd] = 0;
    uVar1 = param_1[5];
    if ((bVar3) && (uVar1 < 0x10)) {
      param_1[(long)(int)uVar1 * 0x30 + 0x21] = param_1[(long)(int)uVar1 * 0x30 + 0x21] + 1;
    }
    else if ((int)uVar1 < 0xf) {
      param_1[5] = uVar1 + 1;
      param_1[6] = param_1[6] + 1;
    }
    else {
      *(byte *)(param_1 + 1) = *(byte *)(param_1 + 1) | 0x80;
    }
    cVar4 = FUN_000e4d70(6,1);
    if (cVar4 != '\0') {
      if ((DAT_02802d48 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_02802d48), iVar5 != 0)) {
        DAT_02802d40 = FUN_000e4a10(s_networking_logic_matchmaking_see_016859e0);
        thunk_FUN_012aa7e6(&DAT_02802d48);
      }
      FUN_01008290(local_178,s_networking_logic_matchmaking_see_016859e0,param_1[5],param_1[0xc]);
      FUN_000e4aa0(DAT_02802d40,local_178);
    }
    if (*(char *)(lVar8 + 0x3c) == '\0') {
      FUN_00b14630(param_1[0x14]);
    }
    lVar8 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      lVar8 = FUN_000694d0();
    }
    *(long *)(param_1 + (long)(int)param_1[5] * 0x30 + 0x1c) = lVar8;
    plVar7 = (long *)FUN_005979c0();
    cVar4 = (**(code **)(*plVar7 + 0x48))(plVar7,*param_1);
    *(byte *)(param_1 + 1) = *(byte *)(param_1 + 1) | 4;
    if (cVar4 == '\0') {
      FUN_00b12000(param_1);
      cVar4 = FUN_000e4d70(6,4);
      if (cVar4 != '\0') {
        if ((DAT_02802d58 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_02802d58), iVar5 != 0)) {
          DAT_02802d50 = FUN_000e4a10(s_networking_logic_matchmaking_see_01685a25);
          thunk_FUN_012aa7e6(&DAT_02802d58);
        }
        FUN_01008290(local_178,s_networking_logic_matchmaking_see_01685a25,param_1[5]);
        FUN_000e4aa0(DAT_02802d50,local_178);
      }
    }
  }
  else {
    iVar6 = FUN_000697a0();
    if (30000 < (uint)(iVar6 - _DAT_02802d20)) {
      cVar4 = FUN_000e4d70(6,1);
      if (cVar4 != '\0') {
        if ((DAT_02802d28 == '\0') && (iVar6 = thunk_FUN_012aa7d6(&DAT_02802d28), iVar6 != 0)) {
          DAT_02802d24 = FUN_000e4a10(s_networking_logic_matchmaking_see_016858bf);
          thunk_FUN_012aa7e6(&DAT_02802d28);
        }
        uVar9 = FUN_00b0da50(iVar5);
        FUN_01008290(local_178,s_networking_logic_matchmaking_see_016858bf,uVar9);
        FUN_000e4aa0(DAT_02802d24,local_178);
      }
      _DAT_02802d20 = FUN_000697a0();
    }
  }
LAB_00b1117e:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

