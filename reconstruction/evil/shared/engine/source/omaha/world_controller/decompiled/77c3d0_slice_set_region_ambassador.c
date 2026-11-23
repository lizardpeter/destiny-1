
void FUN_0077c3d0(long param_1)

{
  int iVar1;
  char cVar2;
  short sVar3;
  int iVar4;
  int iVar5;
  undefined8 uVar6;
  long lVar7;
  long lVar8;
  long lVar9;
  char *pcVar10;
  undefined8 uVar11;
  undefined4 local_6a0 [2];
  undefined4 local_698 [2];
  undefined4 local_690 [2];
  undefined4 local_688 [2];
  undefined4 local_680 [2];
  undefined1 local_678 [256];
  undefined1 local_578 [256];
  undefined1 local_478 [256];
  undefined1 local_378 [256];
  undefined1 local_278 [256];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar2 = FUN_00906f70();
  if ((cVar2 != '\0') || (*(char *)(param_1 + 0x81) != '\0')) {
    FUN_007680f0();
    *(byte *)(param_1 + 0x8a) = *(byte *)(param_1 + 0x8a) & 0xf7;
    uVar6 = thunk_FUN_00768060();
    FUN_0076f710(uVar6,3);
    goto LAB_0077c429;
  }
  lVar7 = FUN_007680f0();
  iVar4 = FUN_0076a860(2);
  lVar8 = FUN_0034e5b0();
  iVar5 = *(int *)(lVar8 + 8);
  iVar1 = *(int *)(lVar8 + 0xc);
  lVar8 = *(long *)(param_1 + 0x568);
  if (lVar8 == -1) {
    lVar8 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      lVar8 = FUN_000694d0();
    }
    *(long *)(param_1 + 0x568) = lVar8;
  }
  if (iVar4 == 5) {
    FUN_0077ca30(param_1);
    pcVar10 = s_matchmaking_disabled_0164f0d2;
LAB_0077c59c:
    FUN_0077cb60(param_1,1,1,pcVar10);
LAB_0077c5ae:
    FUN_0076a760(2);
    FUN_007680f0();
    *(byte *)(param_1 + 0x8a) = *(byte *)(param_1 + 0x8a) & 0xf7;
    uVar6 = thunk_FUN_00768060();
    FUN_0076f710(uVar6,3);
    if ((*(byte *)(param_1 + 0x8a) & 0x20) != 0) goto LAB_0077c429;
    *(byte *)(param_1 + 0x8a) = *(byte *)(param_1 + 0x8a) | 0x20;
    uVar6 = thunk_FUN_00768060();
    uVar11 = 5;
  }
  else {
    if (*(char *)(param_1 + 0x4a9) != '\0') {
      cVar2 = FUN_000e4d70(4,2);
      if (cVar2 != '\0') {
        if ((DAT_026ca880 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_026ca880), iVar5 != 0)) {
          DAT_026ca878 = FUN_000e4a10(s_world_controller_slice_set_trans_0164f0e7);
          thunk_FUN_012aa7e6(&DAT_026ca880);
        }
        uVar6 = FUN_00342a30(lVar7 + 0xa8);
        uVar11 = FUN_003430b0();
        FUN_00344990(local_680,uVar11,*(undefined4 *)(lVar7 + 0xa8));
        FUN_010156f0(local_278,s__8s__HASH__0x_08x__0164efff,uVar6,local_680[0]);
        FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f0e7,local_278);
        FUN_000e4aa0(DAT_026ca878,local_178);
      }
      FUN_0077ca30(param_1);
      pcVar10 = s_matchmaking_aborted_0164f18e;
      goto LAB_0077c59c;
    }
    if (*(char *)(param_1 + 0x499) == '\x02') {
      lVar9 = DAT_026553b0;
      if (DAT_026553a8 == '\0') {
        lVar9 = FUN_000694d0();
      }
      if (lVar9 - lVar8 < (long)(iVar5 - iVar1)) goto LAB_0077c63a;
      cVar2 = FUN_000e4d70(4,3);
      if (cVar2 != '\0') {
        if ((DAT_026ca890 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_026ca890), iVar5 != 0)) {
          DAT_026ca888 = FUN_000e4a10(s_world_controller_slice_set_trans_0164f1a2);
          thunk_FUN_012aa7e6(&DAT_026ca890);
        }
        uVar6 = FUN_00342a30(lVar7 + 0xa8);
        uVar11 = FUN_003430b0();
        FUN_00344990(local_688,uVar11,*(undefined4 *)(lVar7 + 0xa8));
        FUN_010156f0(local_378,s__8s__HASH__0x_08x__0164efff,uVar6,local_688[0]);
        FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f1a2,local_378);
        FUN_000e4aa0(DAT_026ca888,local_178);
      }
      goto LAB_0077c5ae;
    }
LAB_0077c63a:
    if (iVar4 == 0) {
      sVar3 = FUN_00777280(1);
      cVar2 = FUN_000e4d70(4,1);
      if (cVar2 != '\0') {
        if ((DAT_026ca8a0 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_026ca8a0), iVar5 != 0)) {
          DAT_026ca898 = FUN_000e4a10(s_world_controller_slice_set_trans_0164f24c);
          thunk_FUN_012aa7e6(&DAT_026ca8a0);
        }
        uVar6 = FUN_00342a30(lVar7 + 0xa8);
        uVar11 = FUN_003430b0();
        FUN_00344990(local_690,uVar11,*(undefined4 *)(lVar7 + 0xa8));
        FUN_010156f0(local_478,s__8s__HASH__0x_08x__0164efff,uVar6,local_690[0]);
        FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f24c,(int)sVar3,local_478);
        FUN_000e4aa0(DAT_026ca898,local_178);
      }
      FUN_0077ca30(param_1);
      FUN_0077cb60(param_1,1,1,s_starting_ambassador_matchmaking_0164f2bb);
      FUN_0076ab30();
      goto LAB_0077c429;
    }
    cVar2 = FUN_0076a8d0(iVar4);
    if (cVar2 != '\0') {
      cVar2 = FUN_000e4d70(4,4);
      if (cVar2 != '\0') {
        if ((DAT_026ca8b0 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_026ca8b0), iVar5 != 0)) {
          DAT_026ca8a8 = FUN_000e4a10(s_world_controller_slice_set_trans_0164f2db);
          thunk_FUN_012aa7e6(&DAT_026ca8b0);
        }
        uVar6 = FUN_00342a30(lVar7 + 0xa8);
        uVar11 = FUN_003430b0();
        FUN_00344990(local_698,uVar11,*(undefined4 *)(lVar7 + 0xa8));
        FUN_010156f0(local_578,s__8s__HASH__0x_08x__0164efff,uVar6,local_698[0]);
        FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f2db,local_578,iVar4);
        FUN_000e4aa0(DAT_026ca8a8,local_178);
      }
      FUN_0077cb60(param_1,1,0,s_matchmaking_failed_0164f340);
      FUN_0077bb00(param_1,9);
      goto LAB_0077c429;
    }
    if (iVar4 == 1) goto LAB_0077c429;
    cVar2 = FUN_000e4d70(4,1);
    if (cVar2 != '\0') {
      if ((DAT_026ca8c0 == '\0') && (iVar5 = thunk_FUN_012aa7d6(&DAT_026ca8c0), iVar5 != 0)) {
        DAT_026ca8b8 = FUN_000e4a10(s_world_controller_slice_set_trans_0164f353);
        thunk_FUN_012aa7e6(&DAT_026ca8c0);
      }
      uVar6 = FUN_00342a30(lVar7 + 0xa8);
      uVar11 = FUN_003430b0();
      FUN_00344990(local_6a0,uVar11,*(undefined4 *)(lVar7 + 0xa8));
      FUN_010156f0(local_678,s__8s__HASH__0x_08x__0164efff,uVar6,local_6a0[0]);
      FUN_01008290(local_178,s_world_controller_slice_set_trans_0164f353,local_678);
      FUN_000e4aa0(DAT_026ca8b8,local_178);
    }
    FUN_007680f0();
    *(byte *)(param_1 + 0x8a) = *(byte *)(param_1 + 0x8a) & 0xf7;
    uVar6 = thunk_FUN_00768060();
    FUN_0076f710(uVar6,3);
    if ((*(byte *)(param_1 + 0x8a) & 0x40) != 0) goto LAB_0077c429;
    *(byte *)(param_1 + 0x8a) = *(byte *)(param_1 + 0x8a) | 0x40;
    uVar6 = thunk_FUN_00768060();
    uVar11 = 6;
  }
  FUN_0076f630(uVar6,uVar11);
LAB_0077c429:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

