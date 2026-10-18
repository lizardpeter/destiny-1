
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00567940(long param_1,undefined8 param_2,undefined4 param_3,undefined8 param_4,
                 undefined4 param_5,undefined8 param_6,int param_7,undefined8 *param_8)

{
  code *pcVar1;
  ulong uVar2;
  char cVar3;
  undefined4 uVar4;
  int iVar5;
  int iVar6;
  int iVar7;
  undefined4 uVar8;
  long *plVar9;
  long *plVar10;
  long lVar11;
  long *plVar12;
  long lVar13;
  undefined8 uVar14;
  undefined8 uVar15;
  undefined *puVar16;
  undefined8 *puVar17;
  byte bVar18;
  float fVar19;
  float fVar20;
  float fVar21;
  undefined8 local_240;
  long lStack_238;
  undefined8 uStack_230;
  long lStack_228;
  ulong local_220;
  undefined8 uStack_218;
  undefined8 uStack_210;
  undefined8 uStack_208;
  undefined8 local_200;
  undefined8 uStack_1f8;
  undefined8 uStack_1f0;
  undefined8 uStack_1e8;
  undefined8 local_1e0;
  undefined8 uStack_1d8;
  undefined8 uStack_1d0;
  undefined8 uStack_1c8;
  undefined8 local_1c0;
  undefined1 local_1a0 [320];
  long local_60;
  
  bVar18 = 0;
  local_60 = *DAT_01a1f100;
  plVar9 = (long *)FUN_00560590(param_3);
  uVar4 = (**(code **)(*plVar9 + 0x10))(plVar9);
  plVar10 = (long *)FUN_0055af60(uVar4);
  uVar4 = (**(code **)(*plVar10 + 0x28))(plVar10,param_5,param_4);
  fVar19 = (float)*(int *)(param_1 + 0x128) / (float)*(int *)(param_1 + 0x120);
  iVar5 = FUN_000b0020((long)&DAT_01ad5000 +
                       (ulong)*(ushort *)(param_1 + 0x118) * DAT_01ad5010 + DAT_01ad5000);
  iVar7 = *(int *)((long)&DAT_01ad5000 +
                  (ulong)*(ushort *)(param_1 + 0x118) * DAT_01ad5010 + 0x50 + DAT_01ad5000);
  lVar11 = FUN_000b0020((long)&DAT_01ad5000 +
                        (ulong)*(ushort *)(param_1 + 0x81d0) * DAT_01ad5010 + DAT_01ad5000);
  lVar13 = *(long *)((ulong)*(ushort *)(param_1 + 0x81d0) * DAT_01ad5010 + DAT_01ad5000 + 0x1ad5050)
  ;
  if ((DAT_0163b8d4 < fVar19) && (iVar6 = FUN_000697a0(), 30000 < (uint)(iVar6 - _DAT_026babc0))) {
    if ((DAT_026babc8 == '\0') && (iVar6 = thunk_FUN_012aa7d6(&DAT_026babc8), iVar6 != 0)) {
      DAT_026babc4 = FUN_000e4a10(s_networking_investment_bap_messag_0163bfdb);
      thunk_FUN_012aa7e6(&DAT_026babc8);
    }
    FUN_01008290((double)fVar19,local_1a0,s_networking_investment_bap_messag_0163bfdb,param_1 + 8,
                 *(undefined4 *)(param_1 + 0x128),*(undefined4 *)(param_1 + 0x120));
    FUN_000e4aa0(DAT_026babc4,local_1a0);
    _DAT_026babc0 = FUN_000697a0();
  }
  fVar20 = (float)iVar5 / (float)iVar7;
  if ((DAT_0163b8d4 < fVar20) && (iVar7 = FUN_000697a0(), 30000 < (uint)(iVar7 - _DAT_026babd0))) {
    if ((DAT_026babd8 == '\0') && (iVar7 = thunk_FUN_012aa7d6(&DAT_026babd8), iVar7 != 0)) {
      DAT_026babd4 = FUN_000e4a10(s_networking_investment_bap_messag_0163c06b);
      thunk_FUN_012aa7e6(&DAT_026babd8);
    }
    uVar8 = FUN_000b0020((long)&DAT_01ad5000 +
                         (ulong)*(ushort *)(param_1 + 0x118) * DAT_01ad5010 + DAT_01ad5000);
    FUN_01008290((double)fVar20,local_1a0,s_networking_investment_bap_messag_0163c06b,param_1 + 8,
                 uVar8,*(undefined4 *)
                        ((ulong)*(ushort *)(param_1 + 0x118) * DAT_01ad5010 +
                        DAT_01ad5000 + 0x1ad5050));
    FUN_000e4aa0(DAT_026babd4,local_1a0);
    _DAT_026babd0 = FUN_000697a0();
  }
  fVar21 = (float)lVar11 / (float)lVar13;
  if ((_DAT_0163b8d8 < fVar21) && (iVar7 = FUN_000697a0(), 30000 < (uint)(iVar7 - _DAT_026babe0))) {
    if ((DAT_026babe8 == '\0') && (iVar7 = thunk_FUN_012aa7d6(&DAT_026babe8), iVar7 != 0)) {
      DAT_026babe4 = FUN_000e4a10(s_networking_investment_bap_messag_0163c0fa);
      thunk_FUN_012aa7e6(&DAT_026babe8);
    }
    uVar8 = FUN_000b0020((long)&DAT_01ad5000 +
                         (ulong)*(ushort *)(param_1 + 0x81d0) * DAT_01ad5010 + DAT_01ad5000);
    FUN_01008290((double)fVar21,local_1a0,s_networking_investment_bap_messag_0163c0fa,param_1 + 8,
                 uVar8,*(undefined4 *)
                        ((ulong)*(ushort *)(param_1 + 0x81d0) * DAT_01ad5010 +
                        DAT_01ad5000 + 0x1ad5050));
    FUN_000e4aa0(DAT_026babe4,local_1a0);
    _DAT_026babe0 = FUN_000697a0();
  }
  iVar7 = (**(code **)(*plVar9 + 0x30))(plVar9);
  plVar12 = (long *)0x0;
  if (iVar7 != 0) {
    uVar8 = (**(code **)(*plVar9 + 0x30))(plVar9);
    plVar12 = (long *)FUN_0055af60(uVar8);
  }
  cVar3 = (**(code **)(*plVar9 + 0x20))(plVar9,param_4,param_5);
  if (cVar3 == '\0') goto LAB_00568000;
  if (*(int *)(param_1 + 0x128) == *(int *)(param_1 + 0x120)) {
LAB_00567e9e:
    if (*(char *)(param_1 + 0x4134) == '\0') {
      if (*(int *)(param_1 + 0x128) != 0) {
        for (iVar7 = *(int *)(param_1 + 0x124); iVar7 != -1; iVar7 = (iVar7 + 1) % iVar5) {
          plVar9 = (long *)FUN_00560590(*(undefined4 *)
                                         (*(long *)(param_1 + 0x130 + (long)iVar7 * 8) + 4));
          uVar8 = (**(code **)(*plVar9 + 0x10))(plVar9);
          FUN_0055af60(uVar8);
          iVar5 = *(int *)(param_1 + 0x120);
          iVar6 = ((iVar7 - *(int *)(param_1 + 0x124)) + iVar5) % iVar5;
          if ((iVar6 < 0) || (*(int *)(param_1 + 0x128) + -1 <= iVar6)) break;
        }
      }
      *(undefined1 *)(param_1 + 0x4134) = 1;
    }
  }
  else {
    cVar3 = (**(code **)(*plVar10 + 0x38))(plVar10,uVar4);
    if ((cVar3 == '\0') ||
       (((fVar19 <= DAT_0163b8d4 && (fVar20 <= DAT_0163b8d4)) && (fVar21 <= _DAT_0163b8d8)))) {
      if ((*(int *)(param_1 + 0x128) != *(int *)(param_1 + 0x120)) &&
         (lVar13 = FUN_000b0aa0((long)&DAT_01ad5000 +
                                (ulong)*(ushort *)(param_1 + 0x118) * DAT_01ad5010 + DAT_01ad5000,
                                0x88), lVar13 != 0)) {
        iVar7 = (*(int *)(param_1 + 0x124) + *(int *)(param_1 + 0x128)) % *(int *)(param_1 + 0x120);
        *(int *)(param_1 + 0x128) = *(int *)(param_1 + 0x128) + 1;
        *(long *)(param_1 + 0x130 + (long)iVar7 * 8) = lVar13;
        if (iVar7 != -1) {
          local_220 = 0;
          uStack_230 = 0;
          local_1c0 = 0;
          local_240 = 0xffffffff00000000;
          lStack_238 = 0;
          lStack_228 = 0;
          uStack_1d0 = 0;
          uStack_1d8 = 0;
          local_1e0 = 0;
          uStack_1e8 = 0;
          uStack_1f0 = 0;
          uStack_1f8 = 0;
          local_200 = 0;
          uStack_208 = 0;
          uStack_210 = 0;
          uStack_218 = 0;
          uStack_1c8 = 0xffffffffffffffff;
          iVar5 = (**(code **)*plVar9)(plVar9,param_4,param_5);
          lVar13 = 0;
          local_220 = CONCAT44(local_220._4_4_,iVar5);
          if (iVar5 < 1) {
LAB_00568172:
            if (0 < param_7) {
              lStack_238 = FUN_000b0aa0((long)&DAT_01ad5000 +
                                        (ulong)*(ushort *)(param_1 + 0x81d0) * DAT_01ad5010 +
                                        DAT_01ad5000,(long)param_7);
              if (lStack_238 == 0) {
                if ((DAT_026bac18 == '\0') &&
                   (iVar7 = thunk_FUN_012aa7d6(&DAT_026bac18), iVar7 != 0)) {
                  DAT_026bac10 = FUN_000e4a10(s_networking_investment_bap_messag_0163c2e9);
                  thunk_FUN_012aa7e6(&DAT_026bac18);
                }
                uVar14 = (**(code **)(*plVar10 + 0x20))(plVar10);
                uVar15 = (**(code **)(*plVar10 + 0x30))(plVar10,uVar4);
                if (plVar12 == (long *)0x0) {
                  puVar16 = &DAT_01615ab5;
                }
                else {
                  puVar16 = (undefined *)(**(code **)(*plVar12 + 0x20))(plVar12);
                }
                FUN_01008290(local_1a0,s_networking_investment_bap_messag_0163c2e9,param_1 + 8,
                             param_7,param_3,uVar14,uVar15,puVar16);
                uVar8 = DAT_026bac10;
                goto LAB_005683f2;
              }
              uStack_230 = CONCAT44(uStack_230._4_4_,param_7);
              thunk_FUN_012aa7c6(lStack_238,param_6,(long)param_7);
            }
            puVar17 = &uStack_218;
            for (lVar11 = 0xb; lVar11 != 0; lVar11 = lVar11 + -1) {
              *puVar17 = *param_8;
              param_8 = param_8 + (ulong)bVar18 * -2 + 1;
              puVar17 = puVar17 + (ulong)bVar18 * -2 + 1;
            }
            iVar6 = *(int *)(param_1 + 0x8c);
            *(int *)(param_1 + 0x8c) = iVar6 + 1;
            local_240 = CONCAT44(param_3,iVar6);
            uVar14 = DAT_026553b0;
            if (DAT_026553a8 == '\0') {
              uVar14 = FUN_000694d0();
            }
            pcVar1 = *(code **)(*plVar9 + 0x28);
            local_1c0 = uVar14;
            uVar4 = (**(code **)(**(long **)(param_1 + 0x81e0) + 8))();
            (*pcVar1)(plVar9,uVar4,param_4,param_5,lVar13,iVar5);
            thunk_FUN_012aa7c6(*(undefined8 *)(param_1 + 0x130 + (long)iVar7 * 8),&local_240,0x88);
            goto LAB_00568000;
          }
          lVar13 = FUN_000b0aa0((long)&DAT_01ad5000 +
                                (ulong)*(ushort *)(param_1 + 0x81d0) * DAT_01ad5010 + DAT_01ad5000,
                                (long)iVar5);
          lStack_228 = lVar13;
          if (lVar13 != 0) {
            (**(code **)(*plVar9 + 8))(plVar9,param_4,param_5,lVar13,iVar5);
            goto LAB_00568172;
          }
          if ((DAT_026bac08 == '\0') && (iVar7 = thunk_FUN_012aa7d6(&DAT_026bac08), iVar7 != 0)) {
            DAT_026bac00 = FUN_000e4a10(s_networking_investment_bap_messag_0163c23e);
            thunk_FUN_012aa7e6(&DAT_026bac08);
          }
          uVar2 = local_220;
          uVar14 = (**(code **)(*plVar10 + 0x20))(plVar10);
          uVar15 = (**(code **)(*plVar10 + 0x30))(plVar10,uVar4);
          if (plVar12 == (long *)0x0) {
            puVar16 = &DAT_01615ab5;
          }
          else {
            puVar16 = (undefined *)(**(code **)(*plVar12 + 0x20))();
          }
          FUN_01008290(local_1a0,s_networking_investment_bap_messag_0163c23e,param_1 + 8,
                       uVar2 & 0xffffffff,param_3,uVar14,uVar15,puVar16);
          uVar8 = DAT_026bac00;
LAB_005683f2:
          FUN_000e4aa0(uVar8,local_1a0);
          FUN_00569240(param_1,&local_240,plVar9);
          if (lStack_228 != 0) {
            FUN_000b0bd0((long)&DAT_01ad5000 +
                         (ulong)*(ushort *)(param_1 + 0x81d0) * DAT_01ad5010 + DAT_01ad5000);
            lStack_228 = 0;
          }
          if (lStack_238 != 0) {
            FUN_000b0bd0((long)&DAT_01ad5000 +
                         (ulong)*(ushort *)(param_1 + 0x81d0) * DAT_01ad5010 + DAT_01ad5000);
            lStack_238 = 0;
          }
          lVar13 = -1;
          if (*(int *)(param_1 + 0x128) != 0) {
            lVar13 = (long)((*(int *)(param_1 + 0x128) + -1 + *(int *)(param_1 + 0x124)) %
                           *(int *)(param_1 + 0x120));
          }
          FUN_000b0bd0((long)&DAT_01ad5000 +
                       (ulong)*(ushort *)(param_1 + 0x118) * DAT_01ad5010 + DAT_01ad5000,
                       *(undefined8 *)(param_1 + 0x130 + lVar13 * 8));
          *(undefined8 *)(param_1 + 0x130 + lVar13 * 8) = 0;
          *(int *)(param_1 + 0x128) = *(int *)(param_1 + 0x128) + -1;
          goto LAB_00567e9e;
        }
      }
      if ((DAT_026babf8 == '\0') && (iVar7 = thunk_FUN_012aa7d6(&DAT_026babf8), iVar7 != 0)) {
        DAT_026babf0 = FUN_000e4a10(s_networking_investment_bap_messag_0163c191);
        thunk_FUN_012aa7e6(&DAT_026babf8);
      }
      uVar14 = (**(code **)(*plVar10 + 0x20))(plVar10);
      uVar15 = (**(code **)(*plVar10 + 0x30))(plVar10,uVar4);
      if (plVar12 == (long *)0x0) {
        puVar16 = &DAT_01615ab5;
      }
      else {
        puVar16 = (undefined *)(**(code **)(*plVar12 + 0x20))(plVar12);
      }
      FUN_01008290(local_1a0,s_networking_investment_bap_messag_0163c191,param_1 + 8,param_7,param_3
                   ,uVar14,uVar15,puVar16);
      FUN_000e4aa0(DAT_026babf0,local_1a0);
      goto LAB_00567e9e;
    }
  }
  cVar3 = (**(code **)(*plVar10 + 0x38))(plVar10,uVar4);
  if (cVar3 == '\0') {
    if ((DAT_026bac28 == '\0') && (iVar7 = thunk_FUN_012aa7d6(&DAT_026bac28), iVar7 != 0)) {
      DAT_026bac20 = FUN_000e4a10(s_networking_investment_bap_messag_0163c394);
      thunk_FUN_012aa7e6(&DAT_026bac28);
    }
    uVar14 = (**(code **)(*plVar10 + 0x20))(plVar10);
    uVar15 = (**(code **)(*plVar10 + 0x30))(plVar10,uVar4);
    if (plVar12 == (long *)0x0) {
      puVar16 = &DAT_01615ab5;
    }
    else {
      puVar16 = (undefined *)(**(code **)(*plVar12 + 0x20))(plVar12);
    }
    FUN_01008290(local_1a0,s_networking_investment_bap_messag_0163c394,param_1 + 8,param_3,uVar14,
                 uVar15,puVar16);
    FUN_000e4aa0(DAT_026bac20,local_1a0);
    (**(code **)**(undefined8 **)(param_1 + 0x81e0))
              (*(undefined8 **)(param_1 + 0x81e0),1,*(undefined4 *)(param_1 + 0x94),0);
  }
LAB_00568000:
  if (*DAT_01a1f100 != local_60) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

