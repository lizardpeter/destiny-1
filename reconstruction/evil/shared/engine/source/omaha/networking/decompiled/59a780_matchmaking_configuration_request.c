
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8 FUN_0059a780(long param_1,undefined4 param_2)

{
  undefined4 uVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  long *plVar5;
  undefined4 *puVar6;
  long lVar7;
  long lVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  undefined1 uVar12;
  int local_640 [2];
  undefined4 local_638 [2];
  undefined1 local_630 [32];
  undefined1 local_610 [4];
  undefined4 local_60c;
  undefined1 local_608;
  undefined4 local_604;
  undefined1 local_600;
  undefined8 local_5f8;
  undefined1 local_21c;
  undefined1 local_218;
  undefined4 local_214;
  undefined1 local_210;
  undefined4 local_20c;
  undefined1 local_208;
  int local_204;
  ulong local_200 [12];
  undefined8 local_1a0 [40];
  long local_60;
  
  local_60 = *DAT_01a1f100;
  plVar5 = (long *)FUN_0025a550();
  uVar12 = 0;
  if (plVar5 != (long *)0x0) {
    cVar2 = FUN_00599820(param_1);
    if (cVar2 == '\0') {
      cVar2 = FUN_00599a40(param_1 + 0x18);
      if (cVar2 == '\0') {
        iVar4 = FUN_000697a0();
        if ((uint)(iVar4 - _DAT_026bd098) < 0x3e9) goto LAB_0059aee7;
        cVar2 = FUN_000e4d70(6,2);
        if (cVar2 != '\0') {
          if ((DAT_026bd0a0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026bd0a0), iVar4 != 0)) {
            DAT_026bd09c = FUN_000e4a10(s_networking_online_matchmaking_bu_0163f7a9);
            thunk_FUN_012aa7e6(&DAT_026bd0a0);
          }
          FUN_01008290(local_1a0,s_networking_online_matchmaking_bu_0163f7a9);
          FUN_000e4aa0(DAT_026bd09c,local_1a0);
        }
        _DAT_026bd098 = FUN_000697a0();
      }
      else {
        puVar6 = (undefined4 *)(**(code **)(*plVar5 + 0x328))(plVar5,param_2);
        *(undefined1 *)(param_1 + 0x30) = 0;
        *(int *)(param_1 + 0x28) = *(int *)(param_1 + 0x28) + 1;
        *(undefined4 *)(param_1 + 0x2c) = 0;
        thunk_FUN_012aa986(param_1 + 0x38,0,0x420);
        cVar2 = FUN_000b4f80(param_1);
        if (cVar2 != '\0') {
          cVar2 = FUN_000e4d70(6,3);
          if (cVar2 != '\0') {
            if ((DAT_026bd0b0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026bd0b0), iVar4 != 0)) {
              DAT_026bd0a8 = FUN_000e4a10(s_networking_online_matchmaking_bu_0163f81b);
              thunk_FUN_012aa7e6(&DAT_026bd0b0);
            }
            uVar11 = FUN_00058050(param_1);
            lVar7 = FUN_00078970(param_1);
            lVar8 = DAT_026553b0;
            if (DAT_026553a8 == '\0') {
              lVar8 = FUN_000694d0();
            }
            FUN_01008290(local_1a0,s_networking_online_matchmaking_bu_0163f81b,uVar11,lVar8 - lVar7)
            ;
            FUN_000e4aa0(DAT_026bd0a8,local_1a0);
          }
          FUN_0050fa40(param_1);
        }
        if (puVar6 == (undefined4 *)0x0) {
          iVar4 = FUN_000697a0();
          if (1000 < (uint)(iVar4 - _DAT_026bd0b8)) {
            cVar2 = FUN_000e4d70(6,4);
            if (cVar2 != '\0') {
              if ((DAT_026bd0c0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026bd0c0), iVar4 != 0))
              {
                DAT_026bd0bc = FUN_000e4a10(s_networking_online_matchmaking_bu_0163f8ca);
                thunk_FUN_012aa7e6(&DAT_026bd0c0);
              }
              FUN_01008290(local_1a0,s_networking_online_matchmaking_bu_0163f8ca);
              FUN_000e4aa0(DAT_026bd0bc,local_1a0);
            }
            _DAT_026bd0b8 = FUN_000697a0();
          }
          *(undefined4 *)(param_1 + 0x2c) = 1;
        }
        else if (*(char *)((long)puVar6 + 0xa2) == -1) {
          iVar4 = FUN_000697a0();
          if (1000 < (uint)(iVar4 - _DAT_026bd0c8)) {
            cVar2 = FUN_000e4d70(6,4);
            if (cVar2 != '\0') {
              if ((DAT_026bd0d0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026bd0d0), iVar4 != 0))
              {
                DAT_026bd0cc = FUN_000e4a10(s_networking_online_matchmaking_bu_0163f93b);
                thunk_FUN_012aa7e6(&DAT_026bd0d0);
              }
              FUN_01008290(local_1a0,s_networking_online_matchmaking_bu_0163f93b);
              FUN_000e4aa0(DAT_026bd0cc,local_1a0);
            }
            _DAT_026bd0c8 = FUN_000697a0();
          }
          *(undefined4 *)(param_1 + 0x2c) = 6;
        }
        else {
          plVar5 = (long *)FUN_0025a550();
          lVar8 = (**(code **)(*plVar5 + 0x338))(plVar5,*(undefined1 *)((long)puVar6 + 0xa2));
          if (lVar8 == 0) {
            iVar4 = FUN_000697a0();
            if (1000 < (uint)(iVar4 - _DAT_026bd0d8)) {
              cVar2 = FUN_000e4d70(6,4);
              if (cVar2 != '\0') {
                if ((DAT_026bd0e0 == '\0') &&
                   (iVar4 = thunk_FUN_012aa7d6(&DAT_026bd0e0), iVar4 != 0)) {
                  DAT_026bd0dc = FUN_000e4a10(s_networking_online_matchmaking_bu_01638dae);
                  thunk_FUN_012aa7e6(&DAT_026bd0e0);
                }
                FUN_01008290(local_1a0,s_networking_online_matchmaking_bu_01638dae);
                FUN_000e4aa0(DAT_026bd0dc,local_1a0);
              }
              _DAT_026bd0d8 = FUN_000697a0();
            }
            *(undefined4 *)(param_1 + 0x2c) = 7;
          }
          else {
            local_200[0] = local_200[0] & 0xffffffffffffff00;
            FUN_00545b30(local_630,param_2,0xffff);
            FUN_00545fe0(local_638,local_630);
            FUN_00545f40(local_640,local_630);
            lVar8 = FUN_0034e500();
            FUN_005997d0(param_1,*(undefined4 *)(lVar8 + 0x1f8));
            local_200[4] = 0;
            local_200[5] = 0;
            local_200[6] = 0;
            local_200[7] = 0;
            local_200[0] = 0;
            local_200[1] = 0;
            local_200[2] = 0;
            local_200[3] = 0;
            local_200[9] = 0;
            local_200[8] = 0;
            FUN_001271d0(local_200 + 3);
            thunk_FUN_012aa986(local_610,0,0x410);
            local_608 = 1;
            local_604 = 4;
            local_610[0] = 1;
            local_60c = 0xd;
            local_600 = 1;
            local_5f8 = FUN_00058050(param_1);
            local_21c = 1;
            local_218 = 1;
            local_214 = *puVar6;
            if (local_640[0] != -0x7ee3623b) {
              local_208 = 1;
              local_204 = local_640[0];
            }
            local_210 = 1;
            local_20c = local_638[0];
            FUN_00072050(local_1a0,0xffffffff);
            cVar2 = FUN_0055aa80(0,0x1e,local_200,local_610,0x410,local_1a0[0]);
            cVar3 = FUN_000e4d70(6,1);
            if (cVar3 != '\0') {
              if ((DAT_026bd0f0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026bd0f0), iVar4 != 0))
              {
                DAT_026bd0e8 = FUN_000e4a10(s_networking_online_matchmaking_bu_0163f9af);
                thunk_FUN_012aa7e6(&DAT_026bd0f0);
              }
              uVar11 = FUN_00058050(param_1);
              uVar1 = local_214;
              uVar9 = FUN_00079a30(&DAT_01620037,local_638[0]);
              uVar10 = FUN_00079a30(&DAT_01620037,local_640[0]);
              FUN_01008290(local_1a0,s_networking_online_matchmaking_bu_0163f9af,uVar11,uVar1,
                           local_638[0],uVar9,local_640[0],uVar10);
              FUN_000e4aa0(DAT_026bd0e8,local_1a0);
            }
            uVar12 = 1;
            if (cVar2 != '\0') goto LAB_0059aee7;
            cVar2 = FUN_000e4d70(6,4);
            if (cVar2 != '\0') {
              if ((DAT_026bd100 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026bd100), iVar4 != 0))
              {
                DAT_026bd0f8 = FUN_000e4a10(s_networking_online_matchmaking_bu_0163fa83);
                thunk_FUN_012aa7e6(&DAT_026bd100);
              }
              uVar11 = FUN_00058050(param_1);
              FUN_01008290(local_1a0,s_networking_online_matchmaking_bu_0163fa83,uVar11);
              FUN_000e4aa0(DAT_026bd0f8,local_1a0);
            }
            *(undefined4 *)(param_1 + 0x2c) = 3;
            FUN_0050fa40(param_1);
          }
        }
      }
    }
    else {
      iVar4 = FUN_000697a0();
      if ((uint)(iVar4 - _DAT_026bd088) < 0x3e9) goto LAB_0059aee7;
      cVar2 = FUN_000e4d70(6,2);
      if (cVar2 != '\0') {
        if ((DAT_026bd090 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026bd090), iVar4 != 0)) {
          DAT_026bd08c = FUN_000e4a10(s_networking_online_matchmaking_bu_0163f710);
          thunk_FUN_012aa7e6(&DAT_026bd090);
        }
        FUN_01008290(local_1a0,s_networking_online_matchmaking_bu_0163f710);
        FUN_000e4aa0(DAT_026bd08c,local_1a0);
      }
      _DAT_026bd088 = FUN_000697a0();
    }
    uVar12 = 0;
  }
LAB_0059aee7:
  if (*DAT_01a1f100 != local_60) {
    uVar11 = thunk_FUN_012aa7f6();
    return uVar11;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar12);
}

