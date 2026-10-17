
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0077cd20(long param_1)

{
  long lVar1;
  uint uVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  long lVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  long lVar10;
  long lVar11;
  char *pcVar12;
  long *plVar13;
  long lVar14;
  undefined4 local_12b8 [2];
  undefined4 local_12b0 [2];
  undefined4 local_12a8 [2];
  undefined4 local_12a0 [2];
  undefined4 local_1298 [2];
  undefined4 local_1290 [2];
  undefined4 local_1288 [2];
  undefined4 local_1280 [2];
  undefined4 local_1278 [2];
  undefined4 local_1270 [2];
  undefined4 local_1268 [2];
  undefined4 local_1260 [2];
  long local_1258;
  long local_1250;
  undefined4 local_1248 [2];
  undefined8 local_1240;
  undefined4 local_1238 [2];
  undefined4 local_1230 [2];
  undefined4 local_1228 [2];
  undefined8 local_1220;
  undefined1 local_1218 [256];
  undefined1 local_1118 [256];
  undefined1 local_1018 [256];
  undefined1 local_f18 [256];
  undefined1 local_e18 [256];
  undefined1 local_d18 [256];
  undefined1 local_c18 [256];
  undefined1 local_b18 [256];
  undefined1 local_a18 [256];
  undefined1 local_918 [256];
  undefined1 local_818 [256];
  undefined1 local_718 [256];
  long local_618 [10];
  undefined1 local_5c8 [256];
  undefined1 local_4c8 [80];
  undefined1 local_478 [256];
  undefined1 local_378 [256];
  undefined1 local_278 [256];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar3 = FUN_00906f70();
  if ((cVar3 != '\0') || (*(char *)(param_1 + 0x81) != '\0')) {
    FUN_007680f0();
    *(byte *)(param_1 + 0x8a) = *(byte *)(param_1 + 0x8a) & 0xef;
    uVar6 = thunk_FUN_00768060();
    FUN_0076f710(uVar6,4);
    goto LAB_0077cd77;
  }
  lVar7 = FUN_007680f0();
  if (*(char *)(param_1 + 0x570) == '\0') {
    local_1220 = 0;
    cVar3 = FUN_000e4d70(4,1);
    if (cVar3 != '\0') {
      if ((DAT_026ca8d0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca8d0), iVar4 != 0)) {
        DAT_026ca8c8 = FUN_000e4a10(s_world_controller_slice_set_trans_0164f3af);
        thunk_FUN_012aa7e6(&DAT_026ca8d0);
      }
      FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f3af);
      FUN_000e4aa0(DAT_026ca8c8,local_178);
    }
    *(undefined1 *)(param_1 + 0x570) = 1;
    *(undefined8 *)(param_1 + 0x588) = 0xffffffffffffffff;
    *(undefined8 *)(param_1 + 0x580) = 0xffffffffffffffff;
    cVar3 = FUN_00775270(2,&local_1220);
    if (cVar3 != '\0') {
      cVar3 = FUN_000e4d70(4,3);
      if (cVar3 != '\0') {
        if ((DAT_026ca8e0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca8e0), iVar4 != 0)) {
          DAT_026ca8d8 = FUN_000e4a10(s_world_controller_slice_set_trans_0164f3fa);
          thunk_FUN_012aa7e6(&DAT_026ca8e0);
        }
        uVar6 = FUN_00342a30(lVar7 + 0xa8);
        uVar8 = FUN_003430b0();
        FUN_00344990(local_1228,uVar8,*(undefined4 *)(lVar7 + 0xa8));
        FUN_010156f0(local_278,s__8s__HASH__0x_08x__0164efff,uVar6,local_1228[0]);
        FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f3fa,local_278);
        FUN_000e4aa0(DAT_026ca8d8,local_178);
      }
      FUN_00b73600(local_1220);
    }
  }
  lVar1 = lVar7 + 0xa8;
  if (*(char *)(lVar7 + 0xb9) == '\0') {
    lVar10 = FUN_0034e5b0();
    if (*(int *)(param_1 + 0x4bc) == 0) {
      if (*(int *)(param_1 + 0x490) != -1) {
        iVar4 = *(int *)(lVar10 + 0x18);
        cVar3 = FUN_002e9450();
        if (cVar3 != '\0') {
          cVar3 = FUN_000b4f80(param_1 + 0x560);
          if (cVar3 != '\0') {
            lVar10 = *(long *)(param_1 + 0x588);
            if (lVar10 != -1) {
              lVar14 = DAT_026553b0;
              if (DAT_026553a8 == '\0') {
                lVar14 = FUN_000694d0();
              }
              if (lVar14 - lVar10 < (long)iVar4) goto LAB_0077d61a;
            }
            plVar13 = (long *)FUN_0075d560(0,0);
            local_1240 = 0;
            cVar3 = FUN_000e4d70(4,3);
            if (cVar3 != '\0') {
              if ((DAT_026ca910 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca910), iVar4 != 0))
              {
                DAT_026ca908 = FUN_000e4a10(s_world_controller_slice_set_trans_0164f593);
                thunk_FUN_012aa7e6(&DAT_026ca910);
              }
              uVar6 = FUN_00342a30(lVar1);
              uVar8 = FUN_003430b0();
              FUN_00344990(local_1248,uVar8,*(undefined4 *)(lVar7 + 0xa8));
              FUN_010156f0(local_5c8,s__8s__HASH__0x_08x__0164efff,uVar6,local_1248[0]);
              uVar6 = FUN_002ea530(param_1 + 0x4dc);
              uVar8 = FUN_002a35d0(param_1 + 0x560);
              FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f593,local_5c8,uVar6,
                           uVar8,(int)*(char *)(param_1 + 0x49a));
              FUN_000e4aa0(DAT_026ca908,local_178);
            }
            FUN_0077ca30(param_1);
            FUN_0077cb60(param_1,1,1,s_attempting_citizen_join_0164f62c);
            lVar10 = DAT_026553b0;
            if (DAT_026553a8 == '\0') {
              lVar10 = FUN_000694d0();
            }
            *(long *)(param_1 + 0x588) = lVar10;
            local_1240 = (**(code **)(*plVar13 + 0x10))();
            FUN_002e94f0(param_1 + 0x4dc,local_4c8);
            uVar5 = FUN_00084200();
            uVar6 = FUN_00b21de0(uVar5,local_4c8,&local_1240);
            *(undefined8 *)(param_1 + 0x578) = uVar6;
            goto LAB_0077d61a;
          }
        }
      }
      iVar4 = FUN_000697a0();
      if (5000 < (uint)(iVar4 - _DAT_026ca8f8)) {
        cVar3 = FUN_000e4d70(4,0);
        if (cVar3 != '\0') {
          if ((DAT_026ca900 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca900), iVar4 != 0)) {
            DAT_026ca8fc = FUN_000e4a10(s_world_controller_slice_set_trans_0164f518);
            thunk_FUN_012aa7e6(&DAT_026ca900);
          }
          uVar6 = FUN_00342a30(lVar1);
          uVar8 = FUN_003430b0();
          FUN_00344990(local_1238,uVar8,*(undefined4 *)(lVar7 + 0xa8));
          FUN_010156f0(local_478,s__8s__HASH__0x_08x__0164efff,uVar6,local_1238[0]);
          FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f518,local_478);
          FUN_000e4aa0(DAT_026ca8fc,local_178);
        }
        _DAT_026ca8f8 = FUN_000697a0();
      }
    }
    else {
      iVar4 = FUN_000697a0();
      if (15000 < (uint)(iVar4 - _DAT_026ca8e8)) {
        cVar3 = FUN_000e4d70(4,2);
        if (cVar3 != '\0') {
          if ((DAT_026ca8f0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca8f0), iVar4 != 0)) {
            DAT_026ca8ec = FUN_000e4a10(s_world_controller_slice_set_trans_0164f49f);
            thunk_FUN_012aa7e6(&DAT_026ca8f0);
          }
          uVar6 = FUN_00342a30(lVar1);
          uVar8 = FUN_003430b0();
          FUN_00344990(local_1230,uVar8,*(undefined4 *)(lVar7 + 0xa8));
          FUN_010156f0(local_378,s__8s__HASH__0x_08x__0164efff,uVar6,local_1230[0]);
          FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f49f,local_378);
          FUN_000e4aa0(DAT_026ca8ec,local_178);
        }
        _DAT_026ca8e8 = FUN_000697a0();
      }
    }
  }
  else {
    iVar4 = FUN_00b21550(2,*(undefined8 *)(param_1 + 0x578));
    local_1250 = 0;
    FUN_00775270(2,&local_1250);
    if (iVar4 == 6) {
LAB_0077d5f9:
      *(undefined8 *)(param_1 + 0x578) = 0;
      pcVar12 = s_citizen_join_failed_0164f7b8;
LAB_0077d60b:
      FUN_0077cb60(param_1,1,0,pcVar12);
      goto LAB_0077d61a;
    }
    if (iVar4 == 5) {
      uVar5 = FUN_00b21430(2);
      cVar3 = FUN_000e4d70(4,2);
      if (cVar3 != '\0') {
        if ((DAT_026ca940 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca940), iVar4 != 0)) {
          DAT_026ca938 = FUN_000e4a10(s_world_controller_slice_set_trans_0164f7cc);
          thunk_FUN_012aa7e6(&DAT_026ca940);
        }
        uVar6 = FUN_002ea6a0(*(undefined8 *)(param_1 + 0x578));
        uVar8 = FUN_00342a30(lVar1);
        uVar9 = FUN_003430b0();
        FUN_00344990(local_1270,uVar9,*(undefined4 *)(lVar7 + 0xa8));
        FUN_010156f0(local_918,s__8s__HASH__0x_08x__0164efff,uVar8,local_1270[0]);
        FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f7cc,uVar6,local_918,uVar5);
        FUN_000e4aa0(DAT_026ca938,local_178);
      }
      FUN_00b220e0(2);
      goto LAB_0077d61a;
    }
    if (iVar4 == 1) {
      local_1258 = 0;
      lVar10 = param_1 + 0x4dc;
      FUN_002e94f0(lVar10,local_618);
      if (((*(int *)(param_1 + 0x490) != -1) &&
          (*(char *)(param_1 + 0x49a) == *(char *)(param_1 + 0x3b4))) &&
         ((*(char *)(param_1 + 0x499) == '\x01' ||
          ((*(char *)(param_1 + 0x499) == '\x02' &&
           (*(char *)(param_1 + 0x498) != *(char *)(param_1 + 0x13e))))))) {
        cVar3 = FUN_000e4d70(4,3);
        if (cVar3 != '\0') {
          if ((DAT_026ca920 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca920), iVar4 != 0)) {
            DAT_026ca918 = FUN_000e4a10(s_world_controller_slice_set_trans_0164f644);
            thunk_FUN_012aa7e6(&DAT_026ca920);
          }
          uVar6 = FUN_002ea6a0(*(undefined8 *)(param_1 + 0x578));
          uVar8 = FUN_00342a30(lVar1);
          uVar9 = FUN_003430b0();
          FUN_00344990(local_1260,uVar9,*(undefined4 *)(lVar7 + 0xa8));
          FUN_010156f0(local_718,s__8s__HASH__0x_08x__0164efff,uVar8,local_1260[0]);
          if (local_1250 == 0) {
            pcVar12 = s_DISCONNECTED_0164f6e0;
          }
          else {
            pcVar12 = (char *)FUN_00b6db70();
          }
          uVar8 = FUN_002ea530(lVar10);
          FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f644,uVar6,local_718,pcVar12
                       ,uVar8);
          FUN_000e4aa0(DAT_026ca918,local_178);
        }
        FUN_00b22190(2);
        *(undefined8 *)(param_1 + 0x578) = 0;
        pcVar12 = s_citizen_join_aborted_due_to_amba_0164f6ed;
        goto LAB_0077d60b;
      }
      if ((((local_1250 != 0) && (cVar3 = FUN_00b74210(local_1250,&local_1258), cVar3 != '\0')) &&
          (cVar3 = FUN_0005ce00(&local_1258,8), cVar3 == '\0')) && (local_1258 != local_618[0])) {
        cVar3 = FUN_000e4d70(4,3);
        if (cVar3 != '\0') {
          if ((DAT_026ca930 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca930), iVar4 != 0)) {
            DAT_026ca928 = FUN_000e4a10(s_world_controller_slice_set_trans_0164f718);
            thunk_FUN_012aa7e6(&DAT_026ca930);
          }
          uVar6 = FUN_002ea6a0(*(undefined8 *)(param_1 + 0x578));
          uVar8 = FUN_00342a30(lVar1);
          uVar9 = FUN_003430b0();
          FUN_00344990(local_1268,uVar9,*(undefined4 *)(lVar7 + 0xa8));
          FUN_010156f0(local_818,s__8s__HASH__0x_08x__0164efff,uVar8,local_1268[0]);
          uVar8 = FUN_00b6db70(local_1250);
          uVar9 = FUN_002ea530(lVar10);
          FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f718,uVar6,local_818,uVar8,
                       uVar9);
          FUN_000e4aa0(DAT_026ca928,local_178);
        }
        *(undefined8 *)(param_1 + 0x578) = 0;
        FUN_00b22190(2);
        FUN_0077cb60(param_1,1,0,s_citizen_join_failed_0164f7b8);
      }
      goto LAB_0077d61a;
    }
    if (local_1250 == 0) {
      cVar3 = FUN_000e4d70(4,1);
      if (cVar3 != '\0') {
        if ((DAT_026ca950 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca950), iVar4 != 0)) {
          DAT_026ca948 = FUN_000e4a10(s_world_controller_slice_set_trans_0164f843);
          thunk_FUN_012aa7e6(&DAT_026ca950);
        }
        uVar6 = FUN_002ea6a0(*(undefined8 *)(param_1 + 0x578));
        uVar8 = FUN_00342a30(lVar1);
        uVar9 = FUN_003430b0();
        FUN_00344990(local_1278,uVar9,*(undefined4 *)(lVar7 + 0xa8));
        FUN_010156f0(local_a18,s__8s__HASH__0x_08x__0164efff,uVar8,local_1278[0]);
        FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f843,uVar6,local_a18);
        FUN_000e4aa0(DAT_026ca948,local_178);
      }
      FUN_00b22190(2);
      goto LAB_0077d5f9;
    }
    uVar2 = *(uint *)(local_1250 + 0x8c48);
    switch(uVar2) {
    case 3:
    case 5:
    case 7:
      goto switchD_0077d50c_caseD_3;
    default:
      goto switchD_0077d50c_caseD_4;
    case 8:
      pcVar12 = (char *)(local_1250 + 0x8c50);
      break;
    case 9:
      pcVar12 = (char *)(local_1250 + 0x8c54);
    }
    if (*pcVar12 == '\0') {
switchD_0077d50c_caseD_4:
      if (iVar4 != 3) {
        if (iVar4 == 2) {
          cVar3 = FUN_000e4d70(4,0);
          if (cVar3 != '\0') {
            if ((DAT_026ca970 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca970), iVar4 != 0)) {
              DAT_026ca968 = FUN_000e4a10(s_world_controller_slice_set_trans_0164f956);
              thunk_FUN_012aa7e6(&DAT_026ca970);
            }
            uVar6 = FUN_002ea6a0(*(undefined8 *)(param_1 + 0x578));
            uVar8 = FUN_00342a30(lVar1);
            uVar9 = FUN_003430b0();
            FUN_00344990(local_1288,uVar9,*(undefined4 *)(lVar7 + 0xa8));
            FUN_010156f0(local_c18,s__8s__HASH__0x_08x__0164efff,uVar8,local_1288[0]);
            FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f956,uVar6,local_c18);
            FUN_000e4aa0(DAT_026ca968,local_178);
          }
          FUN_00b21f70(2);
        }
        else if ((uVar2 < 0xb) && ((0x7f0U >> (uVar2 & 0x1f) & 1) != 0)) {
          cVar3 = FUN_00b742d0();
          if (cVar3 == '\0') {
            iVar4 = FUN_000697a0();
            if (1000 < (uint)(iVar4 - _DAT_026ca988)) {
              cVar3 = FUN_000e4d70(4,0);
              if (cVar3 != '\0') {
                if ((DAT_026ca990 == '\0') &&
                   (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca990), iVar4 != 0)) {
                  DAT_026ca98c = FUN_000e4a10(s_world_controller_slice_set_trans_0164fa52);
                  thunk_FUN_012aa7e6(&DAT_026ca990);
                }
                uVar6 = FUN_002ea6a0(*(undefined8 *)(param_1 + 0x578));
                uVar8 = FUN_00342a30(lVar1);
                uVar9 = FUN_003430b0();
                FUN_00344990(local_1298,uVar9,*(undefined4 *)(lVar7 + 0xa8));
                FUN_010156f0(local_e18,s__8s__HASH__0x_08x__0164efff,uVar8,local_1298[0]);
                FUN_01008290(local_178,s_world_controller_slice_set_trans_0164fa52,uVar6,local_e18);
                FUN_000e4aa0(DAT_026ca98c,local_178);
              }
              _DAT_026ca988 = FUN_000697a0();
            }
          }
          else {
            lVar10 = FUN_00b74340(local_1250);
            if (*(int *)(lVar10 + 0x5c + (long)*(int *)(lVar10 + 0x5d0c) * 0x168) == 10) {
              cVar3 = FUN_000e4d70(4,1);
              if (cVar3 != '\0') {
                if ((DAT_026ca9b0 == '\0') &&
                   (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca9b0), iVar4 != 0)) {
                  DAT_026ca9a8 = FUN_000e4a10(s_world_controller_slice_set_trans_0164fb87);
                  thunk_FUN_012aa7e6(&DAT_026ca9b0);
                }
                uVar6 = FUN_002ea6a0(*(undefined8 *)(param_1 + 0x578));
                uVar8 = FUN_00342a30(lVar1);
                uVar9 = FUN_003430b0();
                FUN_00344990(local_12a8,uVar9,*(undefined4 *)(lVar7 + 0xa8));
                FUN_010156f0(local_1018,s__8s__HASH__0x_08x__0164efff,uVar8,local_12a8[0]);
                FUN_01008290(local_178,s_world_controller_slice_set_trans_0164fb87,uVar6,local_1018)
                ;
                FUN_000e4aa0(DAT_026ca9a8,local_178);
              }
              *(undefined1 *)(param_1 + 0x570) = 0;
              *(undefined8 *)(param_1 + 0x578) = 0;
              *(undefined8 *)(param_1 + 0x588) = 0xffffffffffffffff;
              *(undefined8 *)(param_1 + 0x580) = 0xffffffffffffffff;
              FUN_007680f0();
              *(byte *)(param_1 + 0x8a) = *(byte *)(param_1 + 0x8a) & 0xef;
              uVar6 = thunk_FUN_00768060();
              FUN_0076f710(uVar6,4);
              if ((*(byte *)(param_1 + 0x8a) & 0x40) == 0) {
                *(byte *)(param_1 + 0x8a) = *(byte *)(param_1 + 0x8a) | 0x40;
                uVar6 = thunk_FUN_00768060();
                FUN_0076f630(uVar6,6);
              }
            }
            else {
              iVar4 = FUN_000697a0();
              if (1000 < (uint)(iVar4 - _DAT_026ca998)) {
                cVar3 = FUN_000e4d70(4,0);
                if (cVar3 != '\0') {
                  if ((DAT_026ca9a0 == '\0') &&
                     (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca9a0), iVar4 != 0)) {
                    DAT_026ca99c = FUN_000e4a10(s_world_controller_slice_set_trans_0164fad1);
                    thunk_FUN_012aa7e6(&DAT_026ca9a0);
                  }
                  uVar6 = FUN_002ea6a0(*(undefined8 *)(param_1 + 0x578));
                  uVar8 = FUN_00342a30(lVar1);
                  uVar9 = FUN_003430b0();
                  FUN_00344990(local_12a0,uVar9,*(undefined4 *)(lVar7 + 0xa8));
                  FUN_010156f0(local_f18,s__8s__HASH__0x_08x__0164efff,uVar8,local_12a0[0]);
                  FUN_01008290(local_178,s_world_controller_slice_set_trans_0164fad1,uVar6,local_f18
                              );
                  FUN_000e4aa0(DAT_026ca99c,local_178);
                }
                _DAT_026ca998 = FUN_000697a0();
              }
            }
          }
        }
        else {
          iVar4 = FUN_000697a0();
          if (1000 < (uint)(iVar4 - _DAT_026ca978)) {
            cVar3 = FUN_000e4d70(4,0);
            if (cVar3 != '\0') {
              if ((DAT_026ca980 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca980), iVar4 != 0))
              {
                DAT_026ca97c = FUN_000e4a10(s_world_controller_slice_set_trans_0164f9c8);
                thunk_FUN_012aa7e6(&DAT_026ca980);
              }
              uVar6 = FUN_002ea6a0(*(undefined8 *)(param_1 + 0x578));
              uVar8 = FUN_00342a30(lVar1);
              uVar9 = FUN_003430b0();
              FUN_00344990(local_1290,uVar9,*(undefined4 *)(lVar7 + 0xa8));
              FUN_010156f0(local_d18,s__8s__HASH__0x_08x__0164efff,uVar8,local_1290[0]);
              FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f9c8,uVar6,local_d18);
              FUN_000e4aa0(DAT_026ca97c,local_178);
            }
            _DAT_026ca978 = FUN_000697a0();
          }
        }
      }
    }
    else {
switchD_0077d50c_caseD_3:
      iVar4 = FUN_000697a0();
      if (1000 < (uint)(iVar4 - _DAT_026ca958)) {
        cVar3 = FUN_000e4d70(4,1);
        if (cVar3 != '\0') {
          if ((DAT_026ca960 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca960), iVar4 != 0)) {
            DAT_026ca95c = FUN_000e4a10(s_world_controller_slice_set_trans_0164f8de);
            thunk_FUN_012aa7e6(&DAT_026ca960);
          }
          uVar6 = FUN_00342a30(lVar1);
          uVar8 = FUN_003430b0();
          FUN_00344990(local_1280,uVar8,*(undefined4 *)(lVar7 + 0xa8));
          FUN_010156f0(local_b18,s__8s__HASH__0x_08x__0164efff,uVar6,local_1280[0]);
          uVar6 = FUN_00b6db70(local_1250);
          FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f8de,local_b18,uVar6);
          FUN_000e4aa0(DAT_026ca95c,local_178);
        }
        _DAT_026ca958 = FUN_000697a0();
      }
    }
  }
LAB_0077d61a:
  if (*(char *)(param_1 + 0x570) != '\0') {
    lVar10 = FUN_0034e5b0();
    if (*(char *)(lVar7 + 0x14a) < '\x03') {
      *(undefined8 *)(param_1 + 0x580) = 0xffffffffffffffff;
    }
    else {
      lVar14 = (long)*(int *)(lVar10 + 0x1c);
      lVar10 = *(long *)(param_1 + 0x580);
      if (lVar10 == -1) {
        lVar10 = DAT_026553b0;
        if (DAT_026553a8 == '\0') {
          lVar10 = FUN_000694d0();
        }
        *(long *)(param_1 + 0x580) = lVar10;
        cVar3 = FUN_000e4d70(4,1);
        if (cVar3 != '\0') {
          if ((DAT_026ca9c0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca9c0), iVar4 != 0)) {
            DAT_026ca9b8 = FUN_000e4a10(s_world_controller_slice_set_trans_0164fbe3);
            thunk_FUN_012aa7e6(&DAT_026ca9c0);
          }
          uVar6 = FUN_00342a30(lVar1);
          uVar8 = FUN_003430b0();
          FUN_00344990(local_12b0,uVar8,*(undefined4 *)(lVar7 + 0xa8));
          FUN_010156f0(local_1118,s__8s__HASH__0x_08x__0164efff,uVar6,local_12b0[0]);
          FUN_01008290(local_178,s_world_controller_slice_set_trans_0164fbe3,local_1118,lVar14);
          FUN_000e4aa0(DAT_026ca9b8,local_178);
        }
      }
      else {
        lVar11 = DAT_026553b0;
        if (DAT_026553a8 == '\0') {
          lVar11 = FUN_000694d0();
        }
        if (lVar14 < lVar11 - lVar10) {
          cVar3 = FUN_000e4d70(4,4);
          if (cVar3 != '\0') {
            if ((DAT_026ca9d0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca9d0), iVar4 != 0)) {
              DAT_026ca9c8 = FUN_000e4a10(s_world_controller_slice_set_trans_0164fc77);
              thunk_FUN_012aa7e6(&DAT_026ca9d0);
            }
            uVar6 = FUN_00342a30(lVar1);
            uVar8 = FUN_003430b0();
            FUN_00344990(local_12b8,uVar8,*(undefined4 *)(lVar7 + 0xa8));
            FUN_010156f0(local_1218,s__8s__HASH__0x_08x__0164efff,uVar6,local_12b8[0]);
            FUN_01008290(local_178,s_world_controller_slice_set_trans_0164fc77,local_1218,lVar14);
            FUN_000e4aa0(DAT_026ca9c8,local_178);
          }
          *(undefined8 *)(param_1 + 0x578) = 0;
          FUN_0077bb00(param_1,0xc);
        }
      }
    }
  }
LAB_0077cd77:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

