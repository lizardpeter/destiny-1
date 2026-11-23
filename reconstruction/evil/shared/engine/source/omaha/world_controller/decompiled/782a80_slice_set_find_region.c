
void FUN_00782a80(long param_1,uint param_2)

{
  int *piVar1;
  int *piVar2;
  int *piVar3;
  char cVar4;
  undefined4 uVar5;
  int iVar6;
  long lVar7;
  undefined8 uVar8;
  undefined8 uVar9;
  long lVar10;
  long lVar11;
  bool bVar12;
  undefined4 local_8d0 [2];
  undefined4 local_8c8 [2];
  undefined4 local_8c0 [2];
  undefined4 local_8b8 [2];
  undefined8 local_8b0;
  undefined8 local_8a8;
  undefined4 local_8a0 [2];
  undefined8 local_898;
  undefined4 local_890 [2];
  undefined8 local_888;
  undefined4 local_880 [2];
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
  piVar1 = (int *)(param_1 + 0x3b8);
  piVar2 = (int *)(param_1 + 0x90);
  if (param_2 == 0) {
    lVar7 = FUN_00775180(2);
  }
  else {
    lVar7 = FUN_00772ec0();
    piVar1 = (int *)(param_1 + 0x490);
    piVar2 = (int *)(param_1 + 0x130);
  }
  lVar10 = 0;
  if (*(uint *)(lVar7 + 0x8c48) < 0xb) {
    lVar10 = 0;
    if ((0x3f0U >> (*(uint *)(lVar7 + 0x8c48) & 0x1f) & 1) != 0) {
      lVar10 = lVar7 + 0x6b28;
    }
  }
  bVar12 = param_2 != 0;
  uVar5 = FUN_0075cbe0(1,bVar12);
  FUN_0075d560(1,bVar12);
  FUN_0075edd0(1,bVar12);
  lVar11 = lVar10 + 0x390;
  if (lVar10 == 0) {
    lVar11 = 0;
  }
  if (*(char *)((long)piVar2 + 0x11) == '\x02') {
    if (*(int *)(lVar7 + 0x8c48) == 6) {
      FUN_00b8f690(lVar10 + 0xcd8);
    }
    piVar3 = piVar2 + 0x26;
    cVar4 = FUN_000b4f80(piVar3);
    if ((cVar4 != '\0') && ((param_2 != 0 || (*(char *)(param_1 + 0x89) != '\x04')))) {
      cVar4 = FUN_0075cd90(uVar5);
      if (cVar4 == '\0') {
        if (lVar10 == 0) goto LAB_00782e3f;
        cVar4 = FUN_00b8f690(lVar11);
        if (cVar4 == '\0') {
LAB_00782fc8:
          cVar4 = FUN_000e4d70(4,4);
          if (cVar4 != '\0') {
            if ((DAT_026cae70 == '\0') && (iVar6 = thunk_FUN_012aa7d6(&DAT_026cae70), iVar6 != 0)) {
              DAT_026cae68 = FUN_000e4a10(s_world_controller_slice_set_trans_01652145);
              thunk_FUN_012aa7e6(&DAT_026cae70);
            }
            uVar8 = FUN_00342a30(piVar2);
            uVar9 = FUN_003430b0();
            FUN_00344990(local_890,uVar9,*piVar2);
            FUN_010156f0(local_378,s__8s__HASH__0x_08x__0164efff,uVar8,local_890[0]);
            FUN_01008290(local_178,s_world_controller_slice_set_trans_01652145,local_378,
                         (&PTR_s_CURRENT_019452f0)[param_2]);
            uVar5 = DAT_026cae68;
LAB_00783095:
            FUN_000e4aa0(uVar5,local_178);
          }
        }
        else {
          local_888 = FUN_00b8f0f0(lVar11);
          cVar4 = FUN_000b4f80(&local_888);
          if (cVar4 == '\0') goto LAB_00782fc8;
          cVar4 = FUN_00b8f690(lVar11);
          if (cVar4 == '\0') {
LAB_00782e3f:
            if ((*piVar1 != -1) &&
               (((*(char *)((long)piVar1 + 10) != *(char *)(param_1 + 0x3b4) ||
                 ((*(char *)((long)piVar1 + 9) != '\x01' &&
                  ((*(char *)((long)piVar1 + 9) != '\x02' ||
                   ((char)piVar1[2] == *(char *)((long)piVar2 + 0xe))))))) &&
                (*(char *)((long)piVar1 + 9) == '\x01')))) {
              local_8b0 = *(undefined8 *)(piVar1 + 0x34);
              cVar4 = FUN_000b4f80(&local_8b0);
              if ((cVar4 != '\0') && (cVar4 = FUN_002a35c0(&local_8b0,piVar3), cVar4 != '\0')) {
                cVar4 = FUN_000e4d70(4,4);
                if (cVar4 != '\0') {
                  if ((DAT_026cae90 == '\0') &&
                     (iVar6 = thunk_FUN_012aa7d6(&DAT_026cae90), iVar6 != 0)) {
                    DAT_026cae88 = FUN_000e4a10(s_world_controller_slice_set_trans_01652280);
                    thunk_FUN_012aa7e6(&DAT_026cae90);
                  }
                  uVar8 = FUN_00342a30(piVar2);
                  uVar9 = FUN_003430b0();
                  FUN_00344990(local_8b8,uVar9,*piVar2);
                  FUN_010156f0(local_578,s__8s__HASH__0x_08x__0164efff,uVar8,local_8b8[0]);
                  uVar8 = FUN_002a35d0(piVar3);
                  uVar9 = FUN_002a35d0(&local_8b0);
                  FUN_01008290(local_178,s_world_controller_slice_set_trans_01652280,local_578,
                               (&PTR_s_CURRENT_019452f0)[param_2],uVar8,uVar9);
                  FUN_000e4aa0(DAT_026cae88,local_178);
                }
                iVar6 = 0x10;
                goto LAB_007830a6;
              }
            }
            goto LAB_007830ab;
          }
          local_898 = FUN_00b8f0f0(lVar11);
          cVar4 = FUN_002a35c0(&local_898,piVar3);
          if (cVar4 == '\0') goto LAB_00782e3f;
          cVar4 = FUN_000e4d70(4,4);
          if (cVar4 != '\0') {
            if ((DAT_026cae80 == '\0') && (iVar6 = thunk_FUN_012aa7d6(&DAT_026cae80), iVar6 != 0)) {
              DAT_026cae78 = FUN_000e4a10(s_world_controller_slice_set_trans_016521e2);
              thunk_FUN_012aa7e6(&DAT_026cae80);
            }
            uVar8 = FUN_00342a30(piVar2);
            uVar9 = FUN_003430b0();
            FUN_00344990(local_8a0,uVar9,*piVar2);
            FUN_010156f0(local_478,s__8s__HASH__0x_08x__0164efff,uVar8,local_8a0[0]);
            uVar8 = FUN_002a35d0(piVar3);
            local_8a8 = FUN_00b8f0f0(lVar11);
            uVar9 = FUN_002a35d0(&local_8a8);
            FUN_01008290(local_178,s_world_controller_slice_set_trans_016521e2,local_478,
                         (&PTR_s_CURRENT_019452f0)[param_2],uVar8,uVar9);
            uVar5 = DAT_026cae78;
            goto LAB_00783095;
          }
        }
        iVar6 = 0x13;
      }
      else {
        cVar4 = FUN_000e4d70(4,4);
        if (cVar4 != '\0') {
          if ((DAT_026cae60 == '\0') && (iVar6 = thunk_FUN_012aa7d6(&DAT_026cae60), iVar6 != 0)) {
            DAT_026cae58 = FUN_000e4a10(s_world_controller_slice_set_trans_016520d4);
            thunk_FUN_012aa7e6(&DAT_026cae60);
          }
          uVar8 = FUN_00342a30(piVar2);
          uVar9 = FUN_003430b0();
          FUN_00344990(local_880,uVar9,*piVar2);
          FUN_010156f0(local_278,s__8s__HASH__0x_08x__0164efff,uVar8,local_880[0]);
          uVar8 = FUN_002a46b0(uVar5);
          FUN_01008290(local_178,s_world_controller_slice_set_trans_016520d4,local_278,
                       (&PTR_s_CURRENT_019452f0)[param_2],uVar8);
          FUN_000e4aa0(DAT_026cae58,local_178);
        }
        iVar6 = 0x12 - (uint)(param_2 == 0);
      }
LAB_007830a6:
      FUN_0077bb00(param_1,iVar6);
    }
  }
LAB_007830ab:
  if (*piVar2 != -1) {
    uVar8 = FUN_003430b0();
    uVar5 = FUN_003454c0(uVar8,*piVar2);
    switch(uVar5) {
    case 0:
    case 5:
      cVar4 = FUN_000e4d70(4,4);
      if (cVar4 != '\0') {
        if ((DAT_026caea0 == '\0') && (iVar6 = thunk_FUN_012aa7d6(&DAT_026caea0), iVar6 != 0)) {
          DAT_026cae98 = FUN_000e4a10(s_world_controller_slice_set_trans_0165230e);
          thunk_FUN_012aa7e6(&DAT_026caea0);
        }
        uVar8 = FUN_00342a30(piVar2);
        uVar9 = FUN_003430b0();
        FUN_00344990(local_8c0,uVar9,*piVar2);
        FUN_010156f0(local_678,s__8s__HASH__0x_08x__0164efff,uVar8,local_8c0[0]);
        FUN_01008290(local_178,s_world_controller_slice_set_trans_0165230e,local_678,
                     (&PTR_s_CURRENT_019452f0)[param_2]);
        FUN_000e4aa0(DAT_026cae98,local_178);
      }
      uVar8 = 0xd;
      break;
    default:
      goto switchD_007830ea_caseD_1;
    case 6:
      cVar4 = FUN_000e4d70(4,4);
      if (cVar4 != '\0') {
        if ((DAT_026caeb0 == '\0') && (iVar6 = thunk_FUN_012aa7d6(&DAT_026caeb0), iVar6 != 0)) {
          DAT_026caea8 = FUN_000e4a10(s_world_controller_slice_set_trans_01652361);
          thunk_FUN_012aa7e6(&DAT_026caeb0);
        }
        uVar8 = FUN_00342a30(piVar2);
        uVar9 = FUN_003430b0();
        FUN_00344990(local_8c8,uVar9,*piVar2);
        FUN_010156f0(local_778,s__8s__HASH__0x_08x__0164efff,uVar8,local_8c8[0]);
        FUN_01008290(local_178,s_world_controller_slice_set_trans_01652361,local_778,
                     (&PTR_s_CURRENT_019452f0)[param_2]);
        FUN_000e4aa0(DAT_026caea8,local_178);
      }
      uVar8 = 0xe;
      break;
    case 7:
      cVar4 = FUN_000e4d70(4,4);
      if (cVar4 != '\0') {
        if ((DAT_026caec0 == '\0') && (iVar6 = thunk_FUN_012aa7d6(&DAT_026caec0), iVar6 != 0)) {
          DAT_026caeb8 = FUN_000e4a10(s_world_controller_slice_set_trans_016523b3);
          thunk_FUN_012aa7e6(&DAT_026caec0);
        }
        uVar8 = FUN_00342a30(piVar2);
        uVar9 = FUN_003430b0();
        FUN_00344990(local_8d0,uVar9,*piVar2);
        FUN_010156f0(local_878,s__8s__HASH__0x_08x__0164efff,uVar8,local_8d0[0]);
        FUN_01008290(local_178,s_world_controller_slice_set_trans_016523b3,local_878,
                     (&PTR_s_CURRENT_019452f0)[param_2]);
        FUN_000e4aa0(DAT_026caeb8,local_178);
      }
      uVar8 = 0xf;
    }
    FUN_0077bb00(param_1,uVar8);
  }
switchD_007830ea_caseD_1:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

