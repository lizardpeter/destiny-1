
void FUN_00778d60(long param_1)

{
  int *piVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  int iVar5;
  int iVar6;
  long lVar7;
  long lVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  uint uVar11;
  char cVar12;
  int *piVar13;
  undefined4 local_9b8 [2];
  undefined4 local_9b0 [2];
  undefined4 local_9a8 [2];
  undefined4 local_9a0 [2];
  undefined4 local_998 [2];
  undefined4 local_990 [2];
  undefined4 local_988 [2];
  undefined4 local_980 [2];
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
  lVar7 = FUN_0075d560(0,0);
  if (lVar7 != 0) {
    lVar8 = FUN_0029c3b0(lVar7);
    iVar4 = FUN_00057e60(lVar8 + 8);
    if (iVar4 != *(int *)(param_1 + 0x3b0)) {
      iVar5 = FUN_002a0870(lVar8);
      cVar3 = FUN_000e4d70(4,0);
      if (cVar3 != '\0') {
        if ((DAT_026cab00 == '\0') && (iVar6 = thunk_FUN_012aa7d6(&DAT_026cab00), iVar6 != 0)) {
          DAT_026caaf8 = FUN_000e4a10(s_world_controller_slice_set_trans_01650660);
          thunk_FUN_012aa7e6(&DAT_026cab00);
        }
        FUN_01008290(local_178,s_world_controller_slice_set_trans_01650660,iVar4);
        FUN_000e4aa0(DAT_026caaf8,local_178);
      }
      *(int *)(param_1 + 0x3b0) = iVar4;
      if (*(int *)(param_1 + 0x3b4) != iVar5) {
        if ((*(int *)(param_1 + 0x3b4) != -1) && (cVar3 = FUN_000e4d70(4,4), cVar3 != '\0')) {
          if ((DAT_026cab10 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cab10), iVar4 != 0)) {
            DAT_026cab08 = FUN_000e4a10(s_world_controller_slice_set_trans_016506d3);
            thunk_FUN_012aa7e6(&DAT_026cab10);
          }
          FUN_01008290(local_178,s_world_controller_slice_set_trans_016506d3,
                       *(undefined4 *)(param_1 + 0x3b4));
          FUN_000e4aa0(DAT_026cab08,local_178);
        }
        *(int *)(param_1 + 0x3b4) = iVar5;
      }
      piVar13 = (int *)(lVar8 + 0x2e50);
      piVar1 = (int *)(param_1 + 0x490);
      lVar8 = param_1 + 0x130;
      uVar11 = 0;
      do {
        iVar4 = *piVar13;
        if (iVar4 == -1) break;
        if (iVar4 == *(int *)(param_1 + 0x98)) {
          thunk_FUN_012aa7c6(param_1 + 0x3b8,piVar13,0xd8);
          iVar4 = *piVar13;
        }
        if ((iVar4 == *(int *)(param_1 + 0x138)) &&
           (*(char *)((long)piVar13 + (long)*(int *)(param_1 + 0x3b4) + 0x38) ==
            *(char *)(param_1 + 0x1d0))) {
          if (iVar4 != *piVar1) {
            cVar3 = FUN_000e4d70(4,0);
            if (cVar3 != '\0') {
              if ((DAT_026cab20 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cab20), iVar4 != 0))
              {
                DAT_026cab18 = FUN_000e4a10(s_world_controller_slice_set_trans_0165073c);
                thunk_FUN_012aa7e6(&DAT_026cab20);
              }
              uVar10 = FUN_00342a30(lVar8);
              uVar9 = FUN_003430b0();
              FUN_00344990(local_980,uVar9,*(undefined4 *)(param_1 + 0x130));
              FUN_010156f0(local_278,s__8s__HASH__0x_08x__0164efff,uVar10,local_980[0]);
              FUN_01008290(local_178,s_world_controller_slice_set_trans_0165073c,local_278);
              FUN_000e4aa0(DAT_026cab18,local_178);
            }
            uVar10 = thunk_FUN_00768060();
            FUN_0076f860(uVar10,0);
            iVar4 = *piVar1;
          }
          if (iVar4 == -1) {
            cVar3 = (char)*(undefined4 *)(param_1 + 0x3b4);
LAB_007791c7:
            cVar12 = *(char *)((long)piVar13 + 10);
LAB_007791cc:
            if ((cVar12 == cVar3) && (*(char *)((long)piVar13 + 9) == '\x01')) {
              cVar3 = FUN_000e4d70(4,3);
              if (cVar3 != '\0') {
                if ((DAT_026cab50 == '\0') &&
                   (iVar4 = thunk_FUN_012aa7d6(&DAT_026cab50), iVar4 != 0)) {
                  DAT_026cab48 = FUN_000e4a10(s_world_controller_slice_set_trans_01650899);
                  thunk_FUN_012aa7e6(&DAT_026cab50);
                }
                uVar10 = FUN_00342a30(lVar8);
                uVar9 = FUN_003430b0();
                FUN_00344990(local_998,uVar9,*(undefined4 *)(param_1 + 0x130));
                FUN_010156f0(local_578,s__8s__HASH__0x_08x__0164efff,uVar10,local_998[0]);
                FUN_01008290(local_178,s_world_controller_slice_set_trans_01650899,local_578);
                FUN_000e4aa0(DAT_026cab48,local_178);
              }
              uVar10 = thunk_FUN_00768060();
              uVar9 = 1;
LAB_007792c5:
              FUN_0076f860(uVar10,uVar9);
            }
          }
          else {
            cVar3 = (char)*(undefined4 *)(param_1 + 0x3b4);
            if (*(char *)(param_1 + 0x49a) != cVar3) goto LAB_007791c7;
            cVar2 = *(char *)(param_1 + 0x499);
            if (cVar2 != '\x02') {
              if (cVar2 == '\x01') {
                cVar12 = *(char *)((long)piVar13 + 10);
                goto LAB_007790d4;
              }
              goto LAB_007791c7;
            }
            cVar12 = *(char *)((long)piVar13 + 10);
            if (*(char *)(param_1 + 0x498) == *(char *)(param_1 + 0x13e)) goto LAB_007791cc;
LAB_007790d4:
            if (cVar12 == *(char *)(param_1 + 0x49a)) {
              if ((cVar2 == '\x02') || (*(char *)((long)piVar13 + 9) != '\x02')) goto LAB_007792ca;
              cVar3 = FUN_000e4d70(4,3);
              if (cVar3 != '\0') {
                if ((DAT_026cab40 == '\0') &&
                   (iVar4 = thunk_FUN_012aa7d6(&DAT_026cab40), iVar4 != 0)) {
                  DAT_026cab38 = FUN_000e4a10(s_world_controller_slice_set_trans_01650837);
                  thunk_FUN_012aa7e6(&DAT_026cab40);
                }
                uVar10 = FUN_00342a30(lVar8);
                uVar9 = FUN_003430b0();
                FUN_00344990(local_990,uVar9,*(undefined4 *)(param_1 + 0x130));
                FUN_010156f0(local_478,s__8s__HASH__0x_08x__0164efff,uVar10,local_990[0]);
                FUN_01008290(local_178,s_world_controller_slice_set_trans_01650837,local_478);
                FUN_000e4aa0(DAT_026cab38,local_178);
              }
              uVar10 = thunk_FUN_00768060();
              uVar9 = 2;
              goto LAB_007792c5;
            }
            cVar3 = FUN_000e4d70(4,4);
            if (cVar3 != '\0') {
              if ((DAT_026cab30 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cab30), iVar4 != 0))
              {
                DAT_026cab28 = FUN_000e4a10(s_world_controller_slice_set_trans_0165079e);
                thunk_FUN_012aa7e6(&DAT_026cab30);
              }
              uVar10 = FUN_00342a30(lVar8);
              uVar9 = FUN_003430b0();
              FUN_00344990(local_988,uVar9,*(undefined4 *)(param_1 + 0x130));
              FUN_010156f0(local_378,s__8s__HASH__0x_08x__0164efff,uVar10,local_988[0]);
              FUN_01008290(local_178,s_world_controller_slice_set_trans_0165079e,local_378);
              FUN_000e4aa0(DAT_026cab28,local_178);
            }
          }
LAB_007792ca:
          if (piVar13[0xb] == 0) {
LAB_007793c5:
            if (*(int *)(param_1 + 0x4bc) != 0) {
              cVar3 = FUN_000e4d70(4,3);
              if (cVar3 != '\0') {
                if ((DAT_026cab70 == '\0') &&
                   (iVar4 = thunk_FUN_012aa7d6(&DAT_026cab70), iVar4 != 0)) {
                  DAT_026cab68 = FUN_000e4a10(s_world_controller_slice_set_trans_01650954);
                  thunk_FUN_012aa7e6(&DAT_026cab70);
                }
                uVar10 = FUN_00342a30(lVar8);
                uVar9 = FUN_003430b0();
                FUN_00344990(local_9a8,uVar9,*(undefined4 *)(param_1 + 0x130));
                FUN_010156f0(local_778,s__8s__HASH__0x_08x__0164efff,uVar10,local_9a8[0]);
                FUN_01008290(local_178,s_world_controller_slice_set_trans_01650954,local_778);
                FUN_000e4aa0(DAT_026cab68,local_178);
              }
              uVar10 = thunk_FUN_00768060();
              FUN_0076f860(uVar10,6);
            }
          }
          else if (*(int *)(param_1 + 0x4bc) == 0) {
            cVar3 = FUN_000e4d70(4,3);
            if (cVar3 != '\0') {
              if ((DAT_026cab60 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cab60), iVar4 != 0))
              {
                DAT_026cab58 = FUN_000e4a10(s_world_controller_slice_set_trans_016508fa);
                thunk_FUN_012aa7e6(&DAT_026cab60);
              }
              uVar10 = FUN_00342a30(lVar8);
              uVar9 = FUN_003430b0();
              FUN_00344990(local_9a0,uVar9,*(undefined4 *)(param_1 + 0x130));
              FUN_010156f0(local_678,s__8s__HASH__0x_08x__0164efff,uVar10,local_9a0[0]);
              FUN_01008290(local_178,s_world_controller_slice_set_trans_016508fa,local_678);
              FUN_000e4aa0(DAT_026cab58,local_178);
            }
            uVar10 = thunk_FUN_00768060();
            FUN_0076f860(uVar10,5);
            if (piVar13[0xb] == 0) goto LAB_007793c5;
          }
          if ((char)piVar13[1] == '\x01') {
            cVar3 = FUN_002e9570(param_1 + 0x4dc,piVar13 + 0x13);
            if (cVar3 == '\0') {
              cVar3 = FUN_000e4d70(4,1);
              if (cVar3 != '\0') {
                if ((DAT_026cab80 == '\0') &&
                   (iVar4 = thunk_FUN_012aa7d6(&DAT_026cab80), iVar4 != 0)) {
                  DAT_026cab78 = FUN_000e4a10(s_world_controller_slice_set_trans_016509ae);
                  thunk_FUN_012aa7e6(&DAT_026cab80);
                }
                uVar10 = FUN_00342a30(lVar8);
                uVar9 = FUN_003430b0();
                FUN_00344990(local_9b0,uVar9,*(undefined4 *)(param_1 + 0x130));
                FUN_010156f0(local_878,s__8s__HASH__0x_08x__0164efff,uVar10,local_9b0[0]);
                uVar10 = FUN_002ea530(param_1 + 0x4dc);
                uVar9 = FUN_002ea530(piVar13 + 0x13);
                FUN_01008290(local_178,s_world_controller_slice_set_trans_016509ae,local_878,uVar10,
                             uVar9);
                FUN_000e4aa0(DAT_026cab78,local_178);
              }
              uVar10 = thunk_FUN_00768060();
              FUN_0076f860(uVar10,7);
            }
            cVar3 = FUN_002a35c0(piVar13 + 0x34,param_1 + 0x560);
            if (cVar3 != '\0') {
              cVar3 = FUN_000e4d70(4,1);
              if (cVar3 != '\0') {
                if ((DAT_026cab90 == '\0') &&
                   (iVar4 = thunk_FUN_012aa7d6(&DAT_026cab90), iVar4 != 0)) {
                  DAT_026cab88 = FUN_000e4a10(s_world_controller_slice_set_trans_01650a28);
                  thunk_FUN_012aa7e6(&DAT_026cab90);
                }
                uVar10 = FUN_00342a30(lVar8);
                uVar9 = FUN_003430b0();
                FUN_00344990(local_9b8,uVar9,*(undefined4 *)(param_1 + 0x130));
                FUN_010156f0(local_978,s__8s__HASH__0x_08x__0164efff,uVar10,local_9b8[0]);
                uVar10 = FUN_002a35d0(param_1 + 0x560);
                uVar9 = FUN_002a35d0(piVar13 + 0x34);
                FUN_01008290(local_178,s_world_controller_slice_set_trans_01650a28,local_978,uVar10,
                             uVar9);
                FUN_000e4aa0(DAT_026cab88,local_178);
              }
              uVar10 = thunk_FUN_00768060();
              FUN_0076f860(uVar10,8);
            }
          }
          thunk_FUN_012aa7c6(piVar1,piVar13,0xd8);
        }
        piVar13 = piVar13 + 0x36;
        uVar11 = uVar11 + 1;
      } while (uVar11 < 0x28);
      uVar10 = FUN_0029c3b0(lVar7);
      lVar7 = FUN_002a0880(uVar10);
      if (lVar7 == 0) {
        *(undefined1 *)(param_1 + 0x1e8) = 0;
      }
      else {
        *(bool *)(param_1 + 0x1e8) = *(char *)(lVar7 + 0xf1) == '\0';
      }
    }
  }
  if ((*(int *)(param_1 + 0x3b8) != -1) && (*(int *)(param_1 + 0x3b8) != *(int *)(param_1 + 0x98)))
  {
    cVar3 = FUN_000e4d70(4,0);
    if (cVar3 != '\0') {
      if ((DAT_026caba0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026caba0), iVar4 != 0)) {
        DAT_026cab98 = FUN_000e4a10(s_world_controller_slice_set_trans_01650aa8);
        thunk_FUN_012aa7e6(&DAT_026caba0);
      }
      FUN_01008290(local_178,s_world_controller_slice_set_trans_01650aa8);
      FUN_000e4aa0(DAT_026cab98,local_178);
    }
    thunk_FUN_012aa986(param_1 + 0x3b8,0,0xd8);
    *(undefined4 *)(param_1 + 0x3b8) = 0xffffffff;
    *(undefined1 *)(param_1 + 0x3c2) = 0xff;
    *(undefined1 *)(param_1 + 0x3d0) = 0;
  }
  if ((*(int *)(param_1 + 0x490) != -1) && (*(int *)(param_1 + 0x490) != *(int *)(param_1 + 0x138)))
  {
    cVar3 = FUN_000e4d70(4,0);
    if (cVar3 != '\0') {
      if ((DAT_026cabb0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026cabb0), iVar4 != 0)) {
        DAT_026caba8 = FUN_000e4a10(s_world_controller_slice_set_trans_01650b39);
        thunk_FUN_012aa7e6(&DAT_026cabb0);
      }
      FUN_01008290(local_178,s_world_controller_slice_set_trans_01650b39);
      FUN_000e4aa0(DAT_026caba8,local_178);
    }
    thunk_FUN_012aa986(param_1 + 0x490,0,0xd8);
    *(undefined4 *)(param_1 + 0x490) = 0xffffffff;
    *(undefined1 *)(param_1 + 0x49a) = 0xff;
    *(undefined1 *)(param_1 + 0x4a8) = 0;
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

