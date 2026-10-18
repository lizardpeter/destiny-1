
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00780e60(long param_1)

{
  undefined8 *puVar1;
  char cVar2;
  int iVar3;
  int iVar4;
  int iVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  long lVar9;
  long lVar10;
  long lVar11;
  char *pcVar12;
  char *pcVar13;
  undefined8 local_bd0;
  undefined4 local_bc8 [2];
  undefined4 local_bc0 [2];
  undefined4 local_bb8 [2];
  undefined4 local_bb0 [2];
  undefined4 local_ba8 [2];
  undefined4 local_ba0 [2];
  undefined4 local_b98 [2];
  undefined4 local_b90 [2];
  undefined4 local_b88 [2];
  undefined4 local_b80 [2];
  undefined1 local_b78 [256];
  undefined1 local_a78 [256];
  undefined1 local_978 [256];
  undefined1 local_878 [256];
  undefined1 local_778 [256];
  undefined1 local_678 [256];
  undefined1 local_578 [256];
  undefined1 local_478 [256];
  undefined1 local_378 [256];
  undefined1 local_278 [256];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  iVar3 = 0;
  if (*(int *)(param_1 + 0x130) != -1) {
    uVar6 = FUN_003430b0();
    iVar3 = FUN_003454c0(uVar6,*(undefined4 *)(param_1 + 0x130));
  }
  iVar4 = FUN_0075cbe0(1,1);
  if (*(char *)(param_1 + 0x1d2) == '\x04') {
    uVar6 = 0xffffffffffffffff;
    if ((*(byte *)(param_1 + 0x8a) & 1) != 0) goto LAB_00781988;
    if (iVar3 == 3) {
      lVar9 = param_1 + 0x130;
      if ((*(char *)(param_1 + 0x13c) == '\x01') && (*(char *)(param_1 + 0x141) != '\x02')) {
        iVar4 = FUN_000697a0();
        if (15000 < (uint)(iVar4 - _DAT_026cac68)) {
          cVar2 = FUN_000e4d70(4,2);
          if (cVar2 != '\0') {
            if ((DAT_026cac70 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cac70), iVar4 != 0)) {
              DAT_026cac6c = FUN_000e4a10(s_world_controller_slice_set_trans_0165116a);
              thunk_FUN_012aa7e6(&DAT_026cac70);
            }
            uVar6 = FUN_00342a30(lVar9);
            uVar7 = FUN_003430b0();
            FUN_00344990(local_ba0,uVar7,*(undefined4 *)(param_1 + 0x130));
            FUN_010156f0(local_678,s__8s__HASH__0x_08x__0164efff,uVar6,local_ba0[0]);
            FUN_01008290(local_178,s_world_controller_slice_set_trans_0165116a,local_678);
            FUN_000e4aa0(DAT_026cac6c,local_178);
          }
          _DAT_026cac68 = FUN_000697a0();
          uVar6 = *(undefined8 *)(param_1 + 0x394);
          goto LAB_00781988;
        }
      }
      else if ((*(byte *)(param_1 + 0x8a) & 3) == 0) {
        if (*(char *)(param_1 + 0x13c) == '\0') {
          cVar2 = FUN_00775270(2,0);
          if (cVar2 == '\0') {
            if ((*(char *)(param_1 + 0x13c) != '\0') || (iVar4 == -1)) goto LAB_00781623;
            iVar5 = FUN_000697a0();
            if (15000 < (uint)(iVar5 - _DAT_026cac98)) {
              cVar2 = FUN_000e4d70(4,2);
              if (cVar2 != '\0') {
                if ((DAT_026caca0 == '\0') &&
                   (iVar5 = thunk_FUN_012aa7d6(&DAT_026caca0), iVar5 != 0)) {
                  DAT_026cac9c = FUN_000e4a10(s_world_controller_slice_set_trans_016512fc);
                  thunk_FUN_012aa7e6(&DAT_026caca0);
                }
                uVar6 = FUN_00342a30(lVar9);
                uVar7 = FUN_003430b0();
                FUN_00344990(local_bb8,uVar7,*(undefined4 *)(param_1 + 0x130));
                FUN_010156f0(local_978,s__8s__HASH__0x_08x__0164efff,uVar6,local_bb8[0]);
                uVar6 = FUN_002a46b0(iVar4);
                FUN_01008290(local_178,s_world_controller_slice_set_trans_016512fc,local_978,uVar6);
                FUN_000e4aa0(DAT_026cac9c,local_178);
              }
              _DAT_026cac98 = FUN_000697a0();
              uVar6 = *(undefined8 *)(param_1 + 0x394);
              goto LAB_00781988;
            }
          }
          else {
            iVar4 = FUN_000697a0();
            if (15000 < (uint)(iVar4 - _DAT_026cac88)) {
              cVar2 = FUN_000e4d70(4,2);
              if (cVar2 != '\0') {
                if ((DAT_026cac90 == '\0') &&
                   (iVar4 = thunk_FUN_012aa7d6(&DAT_026cac90), iVar4 != 0)) {
                  DAT_026cac8c = FUN_000e4a10(s_world_controller_slice_set_trans_01651274);
                  thunk_FUN_012aa7e6(&DAT_026cac90);
                }
                uVar6 = FUN_00342a30(lVar9);
                uVar7 = FUN_003430b0();
                FUN_00344990(local_bb0,uVar7,*(undefined4 *)(param_1 + 0x130));
                FUN_010156f0(local_878,s__8s__HASH__0x_08x__0164efff,uVar6,local_bb0[0]);
                FUN_01008290(local_178,s_world_controller_slice_set_trans_01651274,local_878);
                FUN_000e4aa0(DAT_026cac8c,local_178);
              }
              _DAT_026cac88 = FUN_000697a0();
              uVar6 = *(undefined8 *)(param_1 + 0x394);
              goto LAB_00781988;
            }
          }
        }
        else {
LAB_00781623:
          if (((*(int *)(param_1 + 0x490) != -1) &&
              (*(char *)(param_1 + 0x4c8 + (long)*(int *)(param_1 + 0x3b4)) ==
               *(char *)(param_1 + 0x1d0))) || (lVar10 = FUN_0075d560(0,0), lVar10 == 0)) {
            if ((*(byte *)(param_1 + 0x8a) & 0x80) == 0) {
              if ((*(byte *)(param_1 + 0x8a) & 4) != 0) {
                FUN_007680f0();
                *(byte *)(param_1 + 0x8a) = *(byte *)(param_1 + 0x8a) & 0xfb;
                uVar7 = thunk_FUN_00768060();
                FUN_0076f710(uVar7,2);
              }
              cVar2 = FUN_000e4d70(4,2);
              if (cVar2 != '\0') {
                if ((DAT_026cacc0 == '\0') &&
                   (iVar4 = thunk_FUN_012aa7d6(&DAT_026cacc0), iVar4 != 0)) {
                  DAT_026cacb8 = FUN_000e4a10(s_world_controller_slice_set_trans_01651429);
                  thunk_FUN_012aa7e6(&DAT_026cacc0);
                }
                uVar7 = FUN_00342a30(lVar9);
                uVar8 = FUN_003430b0();
                FUN_00344990(local_bc8,uVar8,*(undefined4 *)(param_1 + 0x130));
                FUN_010156f0(local_b78,s__8s__HASH__0x_08x__0164efff,uVar7,local_bc8[0]);
                FUN_01008290(local_178,s_world_controller_slice_set_trans_01651429,local_b78);
                FUN_000e4aa0(DAT_026cacb8,local_178);
              }
              if (-1 < (char)*(byte *)(param_1 + 0x8a)) {
                *(byte *)(param_1 + 0x8a) = *(byte *)(param_1 + 0x8a) | 0x80;
                uVar7 = thunk_FUN_00768060();
                FUN_0076f630(uVar7,7);
              }
              if (*(char *)(param_1 + 0x89) == '\x03') {
                lVar9 = *(long *)(param_1 + 0x358);
                lVar10 = DAT_026553b0;
                if (DAT_026553a8 == '\0') {
                  lVar10 = FUN_000694d0();
                }
                lVar11 = FUN_0034e5b0();
                if (lVar10 - lVar9 < (long)*(int *)(lVar11 + 0x24)) {
                  uVar7 = thunk_FUN_00768060();
                  FUN_0076f860(uVar7,0xb);
                }
              }
            }
            goto LAB_00781988;
          }
          iVar4 = FUN_000697a0();
          if (15000 < (uint)(iVar4 - _DAT_026caca8)) {
            cVar2 = FUN_000e4d70(4,2);
            if (cVar2 != '\0') {
              if ((DAT_026cacb0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cacb0), iVar4 != 0))
              {
                DAT_026cacac = FUN_000e4a10(s_world_controller_slice_set_trans_01651397);
                thunk_FUN_012aa7e6(&DAT_026cacb0);
              }
              uVar6 = FUN_00342a30(lVar9);
              uVar7 = FUN_003430b0();
              FUN_00344990(local_bc0,uVar7,*(undefined4 *)(param_1 + 0x130));
              FUN_010156f0(local_a78,s__8s__HASH__0x_08x__0164efff,uVar6,local_bc0[0]);
              FUN_01008290(local_178,s_world_controller_slice_set_trans_01651397,local_a78);
              FUN_000e4aa0(DAT_026cacac,local_178);
            }
            _DAT_026caca8 = FUN_000697a0();
            uVar6 = *(undefined8 *)(param_1 + 0x394);
            goto LAB_00781988;
          }
        }
      }
      else {
        iVar4 = FUN_000697a0();
        if (15000 < (uint)(iVar4 - _DAT_026cac78)) {
          cVar2 = FUN_000e4d70(4,2);
          if (cVar2 != '\0') {
            if ((DAT_026cac80 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cac80), iVar4 != 0)) {
              DAT_026cac7c = FUN_000e4a10(s_world_controller_slice_set_trans_016511f5);
              thunk_FUN_012aa7e6(&DAT_026cac80);
            }
            uVar6 = FUN_00342a30(lVar9);
            uVar7 = FUN_003430b0();
            FUN_00344990(local_ba8,uVar7,*(undefined4 *)(param_1 + 0x130));
            FUN_010156f0(local_778,s__8s__HASH__0x_08x__0164efff,uVar6,local_ba8[0]);
            FUN_01008290(local_178,s_world_controller_slice_set_trans_016511f5,local_778);
            FUN_000e4aa0(DAT_026cac7c,local_178);
          }
          _DAT_026cac78 = FUN_000697a0();
          uVar6 = *(undefined8 *)(param_1 + 0x394);
          goto LAB_00781988;
        }
      }
    }
    else {
      if (iVar3 - 5U < 3) {
        iVar4 = FUN_000697a0();
        if (15000 < (uint)(iVar4 - _DAT_026cac48)) {
          cVar2 = FUN_000e4d70(4,4);
          if (cVar2 != '\0') {
            if ((DAT_026cac50 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cac50), iVar4 != 0)) {
              DAT_026cac4c = FUN_000e4a10(s_world_controller_slice_set_trans_01651093);
              thunk_FUN_012aa7e6(&DAT_026cac50);
            }
            uVar7 = FUN_00342a30(param_1 + 0x130);
            uVar8 = FUN_003430b0();
            FUN_00344990(local_b90,uVar8,*(undefined4 *)(param_1 + 0x130));
            FUN_010156f0(local_478,s__8s__HASH__0x_08x__0164efff,uVar7,local_b90[0]);
            FUN_01008290(local_178,s_world_controller_slice_set_trans_01651093,local_478,iVar3);
            FUN_000e4aa0(DAT_026cac4c,local_178);
          }
          _DAT_026cac48 = FUN_000697a0();
        }
        goto LAB_00781988;
      }
      iVar4 = FUN_000697a0();
      if (15000 < (uint)(iVar4 - _DAT_026cac58)) {
        cVar2 = FUN_000e4d70(4,2);
        if (cVar2 != '\0') {
          if ((DAT_026cac60 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cac60), iVar4 != 0)) {
            DAT_026cac5c = FUN_000e4a10(s_world_controller_slice_set_trans_016510ed);
            thunk_FUN_012aa7e6(&DAT_026cac60);
          }
          uVar6 = FUN_00342a30(param_1 + 0x130);
          uVar7 = FUN_003430b0();
          FUN_00344990(local_b98,uVar7,*(undefined4 *)(param_1 + 0x130));
          FUN_010156f0(local_578,s__8s__HASH__0x_08x__0164efff,uVar6,local_b98[0]);
          FUN_01008290(local_178,s_world_controller_slice_set_trans_016510ed,local_578);
          FUN_000e4aa0(DAT_026cac5c,local_178);
        }
        _DAT_026cac58 = FUN_000697a0();
        uVar6 = *(undefined8 *)(param_1 + 0x394);
        goto LAB_00781988;
      }
    }
  }
  else {
    uVar6 = 0xffffffffffffffff;
    if (*(char *)(param_1 + 0x390) == '\0') goto LAB_00781988;
    lVar9 = FUN_0034e3c0();
    cVar2 = *(char *)(lVar9 + 0x90);
    iVar4 = FUN_000697a0();
    if (cVar2 != '\0') {
      if (30000 < (uint)(iVar4 - _DAT_026cac28)) {
        cVar2 = FUN_000e4d70(4,3);
        if (cVar2 != '\0') {
          if ((DAT_026cac30 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cac30), iVar4 != 0)) {
            DAT_026cac2c = FUN_000e4a10(s_world_controller_slice_set_trans_01650f5e);
            thunk_FUN_012aa7e6(&DAT_026cac30);
          }
          uVar7 = FUN_00342a30(param_1 + 0x130);
          uVar8 = FUN_003430b0();
          FUN_00344990(local_b80,uVar8,*(undefined4 *)(param_1 + 0x130));
          FUN_010156f0(local_278,s__8s__HASH__0x_08x__0164efff,uVar7,local_b80[0]);
          FUN_01008290(local_178,s_world_controller_slice_set_trans_01650f5e,local_278,
                       (&PTR_DAT_019451e0)[*(char *)(param_1 + 0x1d2)]);
          FUN_000e4aa0(DAT_026cac2c,local_178);
        }
        _DAT_026cac28 = FUN_000697a0();
      }
      uVar7 = thunk_FUN_00768060();
      FUN_0076f940(uVar7);
      goto LAB_00781988;
    }
    if (30000 < (uint)(iVar4 - _DAT_026cac38)) {
      cVar2 = FUN_000e4d70(4,2);
      if (cVar2 != '\0') {
        if ((DAT_026cac40 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cac40), iVar4 != 0)) {
          DAT_026cac3c = FUN_000e4a10(s_world_controller_slice_set_trans_01651002);
          thunk_FUN_012aa7e6(&DAT_026cac40);
        }
        uVar6 = FUN_00342a30(param_1 + 0x130);
        uVar7 = FUN_003430b0();
        FUN_00344990(local_b88,uVar7,*(undefined4 *)(param_1 + 0x130));
        FUN_010156f0(local_378,s__8s__HASH__0x_08x__0164efff,uVar6,local_b88[0]);
        FUN_01008290(local_178,s_world_controller_slice_set_trans_01651002,local_378,
                     (&PTR_DAT_019451e0)[*(char *)(param_1 + 0x1d2)]);
        FUN_000e4aa0(DAT_026cac3c,local_178);
      }
      _DAT_026cac38 = FUN_000697a0();
    }
  }
  uVar6 = *(undefined8 *)(param_1 + 0x394);
LAB_00781988:
  local_bd0 = uVar6;
  if (((int)uVar6 != *(int *)(param_1 + 0x39c)) ||
     ((int)((ulong)uVar6 >> 0x20) != *(int *)(param_1 + 0x3a0))) {
    puVar1 = (undefined8 *)(param_1 + 0x39c);
    iVar4 = FUN_00071f60(puVar1);
    if (iVar4 != -1) {
      FUN_00bb88d0(*puVar1,0);
      cVar2 = FUN_000e4d70(4,2);
      if (cVar2 != '\0') {
        if ((DAT_026cacd0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cacd0), iVar4 != 0)) {
          DAT_026cacc8 = FUN_000e4a10(s_world_controller_slice_set_trans_01651491);
          thunk_FUN_012aa7e6(&DAT_026cacd0);
        }
        FUN_01008290(local_178,s_world_controller_slice_set_trans_01651491);
        FUN_000e4aa0(DAT_026cacc8,local_178);
      }
      uVar6 = thunk_FUN_00768060();
      FUN_0076f860(uVar6,10);
    }
    iVar4 = FUN_00071f60(&local_bd0);
    if (iVar4 != -1) {
      FUN_00bb88d0(local_bd0,1);
      cVar2 = FUN_000e4d70(4,2);
      if (cVar2 != '\0') {
        if ((DAT_026cace0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cace0), iVar4 != 0)) {
          DAT_026cacd8 = FUN_000e4a10(s_world_controller_slice_set_trans_01651507);
          thunk_FUN_012aa7e6(&DAT_026cace0);
        }
        pcVar12 = s_IN_PROGRESS_0165159d;
        pcVar13 = &DAT_016515a9;
        if (iVar3 != 3) {
          pcVar13 = s_IN_PROGRESS_0165159d;
        }
        if (*(char *)(param_1 + 0x141) == '\x02') {
          pcVar12 = &DAT_016515a9;
        }
        FUN_01008290(local_178,s_world_controller_slice_set_trans_01651507,pcVar13,pcVar12);
        FUN_000e4aa0(DAT_026cacd8,local_178);
      }
      uVar6 = thunk_FUN_00768060();
      FUN_0076f860(uVar6,9);
    }
    *puVar1 = local_bd0;
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

