
bool FUN_00776690(char *param_1)

{
  char cVar1;
  char cVar2;
  undefined1 uVar3;
  int iVar4;
  long lVar5;
  undefined8 uVar6;
  long lVar7;
  char *pcVar8;
  ulong uVar9;
  undefined8 uVar10;
  undefined1 *puVar11;
  long lVar12;
  uint uVar13;
  char *pcVar14;
  ushort uVar15;
  char *pcVar16;
  bool bVar17;
  undefined4 local_2a4;
  undefined8 local_2a0;
  undefined8 local_298;
  undefined1 local_290 [8];
  undefined4 local_288;
  undefined2 auStack_284 [66];
  undefined1 local_200 [320];
  undefined1 local_c0 [2];
  short local_be;
  undefined1 local_bc;
  undefined2 local_ba;
  undefined4 local_b8;
  undefined2 auStack_b4 [66];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  lVar5 = FUN_0075d700();
  if (*(int *)(param_1 + 0x614) == 2) {
    cVar1 = FUN_00b8e0b0(param_1 + 0x74e0);
    goto LAB_00776c97;
  }
  local_b8 = 0;
  local_298 = 0;
  local_2a0 = 0xffffffffffffffff;
  local_2a4 = 0xffffffff;
  lVar12 = *(long *)(PTR_DAT_0197e288 + 8);
  uVar6 = FUN_000e8680(lVar12,0,0xffffffff);
  thunk_FUN_012aa986(local_c0,0,uVar6);
  uVar15 = *(ushort *)(lVar12 + 0x1c) & 0x78;
  bVar17 = uVar15 != 0;
  if (uVar15 == 0) {
    uVar13 = *(uint *)(lVar12 + 0x20);
    if ((*(ushort *)(lVar12 + 0x1c) & 0x40) != 0) {
      lVar7 = FUN_000e8a90(lVar12,local_c0);
      if (lVar7 == 0) {
        uVar13 = uVar13 | 0x5488bf;
      }
      else {
        uVar13 = *(uint *)(lVar7 + 0x20) & 0x5488bf | uVar13;
      }
    }
    bVar17 = (uVar13 & 0xc08070) != 0;
  }
  if (bVar17) {
    FUN_000e6730(lVar12,local_c0,0,0xffffffff,0);
  }
  local_bc = 0xff;
  if (lVar5 != 0) {
    FUN_0029a530(lVar5,local_c0,&local_298,&local_2a0,&local_2a4);
  }
  if (local_be == -1) {
    if (DAT_026ca4e0 == (char *)0x0) {
      pcVar8 = (char *)0x0;
      pcVar16 = (char *)0x0;
      if (param_1 != (char *)0x0) goto LAB_00776844;
      goto LAB_00776a3f;
    }
    pcVar14 = (char *)0x0;
    if (*DAT_026ca4e0 != '\0') {
      pcVar14 = DAT_026ca4e0;
    }
    pcVar8 = DAT_026ca4e0;
    if (pcVar14 == (char *)0x0) {
      pcVar16 = (char *)0x0;
      if (param_1 == (char *)0x0) goto LAB_00776a3f;
LAB_00776844:
      if (pcVar16 == param_1) {
        if (pcVar8 != (char *)0x0) {
          pcVar16 = (char *)0x0;
          if (*pcVar8 != '\0') {
            pcVar16 = pcVar8;
          }
          if (pcVar16 != (char *)0x0) {
            uVar9 = (ulong)*(int *)(pcVar16 + 8);
            goto LAB_007768fd;
          }
        }
      }
      else {
        if (pcVar8 == (char *)0x0) {
          pcVar8 = (char *)0x0;
joined_r0x007768be:
          pcVar16 = (char *)0x0;
          if (param_1 == (char *)0x0) goto LAB_00776a3f;
        }
        else {
          pcVar14 = (char *)0x0;
          if (*pcVar8 != '\0') {
            pcVar14 = pcVar8;
          }
          if (pcVar14 == (char *)0x0) goto joined_r0x007768be;
          pcVar16 = pcVar14 + ((long)*(int *)(pcVar14 + 0x131d0) ^ 1U) * 0x98e0 + 0x131d8;
          if (pcVar14 + ((long)*(int *)(pcVar14 + 8) ^ 1U) * 0x98e0 + 0x10 == param_1)
          goto LAB_00776909;
        }
        if ((pcVar16 == param_1) && (pcVar8 != (char *)0x0)) {
          pcVar16 = (char *)0x0;
          if (*pcVar8 != '\0') {
            pcVar16 = pcVar8;
          }
          if (pcVar16 != (char *)0x0) {
            uVar9 = (long)*(int *)(pcVar16 + 8) ^ 1;
LAB_007768fd:
            pcVar16 = pcVar16 + uVar9 * 0x98e0 + 0x10;
            goto LAB_00776909;
          }
        }
      }
    }
    else {
      pcVar16 = pcVar14 + (long)*(int *)(pcVar14 + 0x131d0) * 0x98e0 + 0x131d8;
      if (pcVar14 + (long)*(int *)(pcVar14 + 8) * 0x98e0 + 0x10 != param_1) goto LAB_00776844;
LAB_00776909:
      pcVar8 = pcVar16 + 0x74e0;
      cVar1 = FUN_00b8f690(pcVar8);
      if (cVar1 != '\0') {
        cVar1 = FUN_000e4d70(9,4);
        if (cVar1 != '\0') {
          if ((DAT_026ca690 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca690), iVar4 != 0)) {
            DAT_026ca688 = FUN_000e4a10(s_world_controller_session_manager_0164e667);
            thunk_FUN_012aa7e6(&DAT_026ca690);
          }
          uVar6 = FUN_00b6db70(param_1);
          uVar10 = FUN_00b6db70(pcVar16);
          FUN_01008290(local_200,s_world_controller_session_manager_0164e667,uVar6,uVar10);
          FUN_000e4aa0(DAT_026ca688,local_200);
        }
        puVar11 = (undefined1 *)FUN_011c3f80(pcVar8);
        local_c0[0] = *puVar11;
        local_be = *(short *)(puVar11 + 2);
        local_bc = puVar11[4];
        lVar5 = 0;
        local_ba = *(undefined2 *)(puVar11 + 6);
        local_b8 = *(undefined4 *)(puVar11 + 8);
        do {
          auStack_b4[lVar5 * 2] = *(undefined2 *)(puVar11 + lVar5 * 4 + 0xc);
          auStack_b4[lVar5 * 2 + 1] = *(undefined2 *)(puVar11 + lVar5 * 4 + 0xe);
          lVar5 = lVar5 + 1;
        } while (lVar5 != 0x20);
        local_298 = FUN_00b8e190(pcVar8);
        local_2a0 = FUN_00b8e1f0(pcVar8);
        local_2a4 = FUN_00b8e220(pcVar8);
      }
    }
LAB_00776a3f:
    if (local_be == -1) {
      lVar5 = FUN_00574ef0();
      thunk_FUN_012aa7c6(local_290,lVar5 + 0x8c,0x8c);
      local_c0[0] = (undefined1)local_290._0_4_;
      lVar12 = 0;
      local_be = SUB42(local_290._0_4_,2);
      local_bc = (undefined1)local_290._4_4_;
      local_ba = SUB42(local_290._4_4_,2);
      local_b8 = local_288;
      do {
        auStack_b4[lVar12 * 2] = auStack_284[lVar12 * 2];
        auStack_b4[lVar12 * 2 + 1] = auStack_284[lVar12 * 2 + 1];
        lVar12 = lVar12 + 1;
      } while (lVar12 != 0x20);
      local_298 = *(undefined8 *)(lVar5 + 0x118);
      local_2a0 = *(undefined8 *)(lVar5 + 0x120);
      local_2a4 = *(undefined4 *)(lVar5 + 0x128);
      cVar1 = FUN_000e4d70(9,4);
      if (cVar1 != '\0') {
        if ((DAT_026ca6a0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca6a0), iVar4 != 0)) {
          DAT_026ca698 = FUN_000e4a10(s_world_controller_session_manager_0164e6db);
          thunk_FUN_012aa7e6(&DAT_026ca6a0);
        }
        uVar6 = FUN_00b6db70(param_1);
        iVar4 = (int)local_be;
        uVar10 = FUN_002ea6a0(local_298);
        FUN_01008290(local_200,s_world_controller_session_manager_0164e6db,uVar6,iVar4,uVar10,
                     local_2a0,local_2a4);
        FUN_000e4aa0(DAT_026ca698,local_200);
      }
      if (local_be == -1) {
        cVar2 = FUN_000e4d70(9,4);
        cVar1 = '\0';
        if (cVar2 != '\0') {
          if ((DAT_026ca6b0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026ca6b0), iVar4 != 0)) {
            DAT_026ca6a8 = FUN_000e4a10(s_world_controller_session_manager_0164e78e);
            thunk_FUN_012aa7e6(&DAT_026ca6b0);
          }
          uVar6 = FUN_00b6db70(param_1);
          cVar1 = '\0';
          FUN_01008290(local_200,s_world_controller_session_manager_0164e78e,uVar6);
          FUN_000e4aa0(DAT_026ca6a8,local_200);
        }
        goto LAB_00776c97;
      }
    }
  }
  param_1 = param_1 + 0x74e0;
  cVar2 = FUN_00b8dcf0(param_1,local_c0);
  cVar1 = '\0';
  if (((cVar2 != '\0') && (cVar2 = FUN_00b8de80(param_1,local_298), cVar2 != '\0')) &&
     (cVar2 = FUN_00b8df10(param_1,local_2a0), cVar2 != '\0')) {
    cVar1 = FUN_00b8dfa0(param_1,local_2a4);
  }
LAB_00776c97:
  if (*DAT_01a1f100 != local_30) {
    uVar3 = thunk_FUN_012aa7f6();
    return (bool)uVar3;
  }
  return cVar1 != '\0';
}

