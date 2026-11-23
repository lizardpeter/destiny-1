
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0059a500(undefined8 param_1,undefined2 *param_2,undefined1 *param_3)

{
  int iVar1;
  char cVar2;
  int iVar3;
  undefined4 uVar4;
  int iVar5;
  long lVar6;
  float fVar7;
  float fVar8;
  undefined1 local_170 [320];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  FUN_00b0dcb0(param_3);
  if ((*(char *)(param_2 + 0xe) != '\0') && (*(int *)(param_2 + 2) != -1)) {
    iVar3 = FUN_0075e450(*param_2);
    FUN_0059b400();
    uVar4 = FUN_0076ac20(*param_2,*(undefined4 *)(param_2 + 2));
    *(undefined4 *)(param_3 + 4) = uVar4;
    *(undefined2 *)(param_3 + 0x24) = *param_2;
    *(undefined4 *)(param_3 + 0x28) = *(undefined4 *)(param_2 + 2);
    param_3[0x38] = *(undefined1 *)(param_2 + 4);
    *(undefined8 *)(param_3 + 0x30) = *(undefined8 *)(param_2 + 8);
    *(undefined4 *)(param_3 + 0x54) = *(undefined4 *)(param_2 + 0xc);
    *(undefined4 *)(param_3 + 0xac) = 1;
    *(undefined4 *)(param_3 + 0xb0) = 0x15;
    *(undefined4 *)(param_3 + 0xb8) = 0xffffffff;
    param_3[0x3c] = 1;
    fVar7 = (float)FUN_002672c0();
    fVar8 = (float)FUN_00267280();
    *(undefined4 *)(param_3 + 0x134) = 2000;
    *(undefined4 *)(param_3 + 0x138) = 2000;
    *(float *)(param_3 + 0x13c) = fVar7 - fVar8;
    *(float *)(param_3 + 0x140) = fVar7 - fVar8;
    *(undefined8 *)(param_3 + 0x144) = 0x45fa000045fa0000;
    cVar2 = FUN_0075b6a0(*(undefined4 *)(param_2 + 2));
    if (cVar2 == '\0') {
      *(undefined4 *)(param_3 + 0x94) = 0;
      iVar5 = 0x14;
      if (iVar3 < 0x15) {
        iVar5 = iVar3;
      }
      *(int *)(param_3 + 0x9c) = iVar5;
      *(undefined4 *)(param_3 + 0xa0) = 1;
      param_3[1] = 0;
    }
    else {
      lVar6 = FUN_0059b510(param_1,*(undefined4 *)(param_2 + 2));
      param_3[1] = 1;
      *(undefined4 *)(param_3 + 8) = *(undefined4 *)(lVar6 + 0x34);
      iVar5 = 0x14;
      if (iVar3 < 0x15) {
        iVar5 = iVar3;
      }
      *(int *)(param_3 + 0x94) = iVar5;
      iVar3 = *(int *)(lVar6 + 0x14);
      *(int *)(param_3 + 0x9c) = iVar3;
      *(undefined4 *)(param_3 + 0xa0) = *(undefined4 *)(lVar6 + 0x1c);
      iVar1 = *(int *)(lVar6 + 0x24);
      if (iVar3 < *(int *)(lVar6 + 0x24)) {
        iVar1 = iVar3;
      }
      *(int *)(param_3 + 0xa4) = iVar1;
      *(undefined4 *)(param_3 + 0x40) = *(undefined4 *)(lVar6 + 0x2c);
      if (iVar3 < iVar5) {
        iVar3 = FUN_000697a0();
        if (5000 < (uint)(iVar3 - _DAT_026bd158)) {
          cVar2 = FUN_000e4d70(6,4);
          if (cVar2 != '\0') {
            if (DAT_026bd160 == '\0') {
              iVar3 = thunk_FUN_012aa7d6(&DAT_026bd160);
              if (iVar3 != 0) {
                DAT_026bd15c = FUN_000e4a10(s_networking_online_matchmaking_bu_0163fd7c);
                thunk_FUN_012aa7e6(&DAT_026bd160);
              }
            }
            FUN_01008290(local_170,s_networking_online_matchmaking_bu_0163fd7c,
                         *(undefined4 *)(param_3 + 0x94),*(undefined4 *)(param_3 + 0x9c));
            FUN_000e4aa0(DAT_026bd15c,local_170);
          }
          _DAT_026bd158 = FUN_000697a0();
        }
        *(undefined4 *)(param_3 + 0x9c) = *(undefined4 *)(param_3 + 0x94);
      }
    }
    *param_3 = 1;
  }
  if (*DAT_01a1f100 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

