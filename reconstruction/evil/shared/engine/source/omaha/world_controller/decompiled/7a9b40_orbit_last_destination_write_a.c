
void FUN_007a9b40(void)

{
  long *plVar1;
  char cVar2;
  uint uVar3;
  int iVar4;
  ulong uVar5;
  undefined8 uVar6;
  long lVar7;
  undefined8 uVar8;
  undefined *puVar9;
  long lVar10;
  ushort uVar11;
  int *piVar12;
  undefined4 *puVar13;
  undefined4 uVar14;
  long lVar15;
  bool bVar16;
  int local_184;
  int local_180 [2];
  undefined1 local_178 [320];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar3 = FUN_0075cfd0();
  if (uVar3 == 0xffffffff) {
LAB_007a9bb4:
    cVar2 = FUN_000e4d70(5,4);
    if (cVar2 == '\0') goto LAB_007a9c25;
    if ((DAT_026d03f0 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026d03f0), iVar4 != 0)) {
      DAT_026d03e8 = FUN_000e4a10(s_world_controller_state_setup_act_0165cebf);
      thunk_FUN_012aa7e6(&DAT_026d03f0);
    }
    FUN_01008290(local_178,s_world_controller_state_setup_act_0165cebf);
    uVar14 = DAT_026d03e8;
  }
  else {
    lVar10 = (ulong)(((uint)((int)uVar3 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar3 >> 0xd) * 0x40;
    lVar15 = *DAT_01a238a0;
    lVar7 = *(long *)(lVar15 + 0x10 + lVar10);
    uVar5 = (ulong)((uVar3 & 0x1fff) * *(int *)(lVar15 + 0x30 + lVar10));
    lVar15 = (lVar7 + uVar5) -
             ((long)*(int *)(lVar15 + 0x34 + lVar10) & *(ulong *)(lVar7 + 8 + uVar5));
    if (lVar15 == 0) goto LAB_007a9bb4;
    if (*(int *)(lVar15 + 0x20) == -0x7ee3623b) {
      cVar2 = FUN_000e4d70(5,4);
      if (cVar2 == '\0') goto LAB_007a9c25;
      if ((DAT_026d0400 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026d0400), iVar4 != 0)) {
        DAT_026d03f8 = FUN_000e4a10(s_world_controller_state_setup_act_0165cf39);
        thunk_FUN_012aa7e6(&DAT_026d0400);
      }
      FUN_01008290(local_178,s_world_controller_state_setup_act_0165cf39);
      uVar14 = DAT_026d03f8;
    }
    else {
      uVar6 = FUN_00587520();
      lVar7 = FUN_0057de80(uVar6);
      lVar10 = FUN_00775770(0);
      local_184 = *(int *)(lVar15 + 0x1c);
      if (local_184 == -0x7ee3623b) {
        local_184 = *(int *)(lVar15 + 0x20);
      }
      if (lVar7 == 0) {
        cVar2 = FUN_000e4d70(5,4);
        if (cVar2 != '\0') {
          if ((DAT_026d0410 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026d0410), iVar4 != 0)) {
            DAT_026d0408 = FUN_000e4a10(s_world_controller_state_setup_act_0165cfbf);
            thunk_FUN_012aa7e6(&DAT_026d0410);
          }
          FUN_01008290(local_178,s_world_controller_state_setup_act_0165cfbf);
          FUN_000e4aa0(DAT_026d0408,local_178);
        }
      }
      else if (*(int *)(lVar7 + 0x480) != local_184) {
        cVar2 = FUN_000e4d70(5,1);
        if (cVar2 != '\0') {
          if ((DAT_026d0420 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026d0420), iVar4 != 0)) {
            DAT_026d0418 = FUN_000e4a10(s_world_controller_state_setup_act_0165d03c);
            thunk_FUN_012aa7e6(&DAT_026d0420);
          }
          uVar6 = FUN_00079a30(&DAT_01620037,*(undefined4 *)(lVar7 + 0x480));
          uVar8 = FUN_00079a30(&DAT_01620037,*(undefined4 *)(lVar15 + 0x20));
          FUN_01008290(local_178,s_world_controller_state_setup_act_0165d03c,uVar6,uVar8);
          FUN_000e4aa0(DAT_026d0418,local_178);
        }
        *(int *)(lVar7 + 0x480) = local_184;
      }
      cVar2 = FUN_00775530(0);
      if (cVar2 == '\0') goto LAB_007a9c25;
      if (lVar10 != 0) {
        plVar1 = (long *)(lVar10 + 0x4b8);
        cVar2 = FUN_00b8f690(plVar1);
        if (cVar2 != '\0') {
          cVar2 = FUN_00b8f690(plVar1);
          piVar12 = (int *)0x0;
          if (cVar2 != '\0') {
            piVar12 = (int *)(lVar10 + 0x59c);
          }
          if (*piVar12 == local_184) goto LAB_007a9c25;
        }
        local_180[0] = -0x7ee3623b;
        cVar2 = FUN_000e4d70(5,1);
        if (cVar2 != '\0') {
          if ((DAT_026d0440 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026d0440), iVar4 != 0)) {
            DAT_026d0438 = FUN_000e4a10(s_world_controller_state_setup_act_0165d14f);
            thunk_FUN_012aa7e6(&DAT_026d0440);
          }
          cVar2 = FUN_00b8f690(plVar1);
          if (cVar2 == '\0') {
            puVar9 = &DAT_01629453;
          }
          else {
            cVar2 = FUN_00b8f690(plVar1);
            puVar13 = (undefined4 *)0x0;
            if (cVar2 != '\0') {
              puVar13 = (undefined4 *)(lVar10 + 0x59c);
            }
            puVar9 = (undefined *)FUN_00079a30(&DAT_01620037,*puVar13);
          }
          uVar6 = FUN_00079a30(&DAT_01620037,local_184);
          FUN_01008290(local_178,s_world_controller_state_setup_act_0165d14f,puVar9,uVar6);
          FUN_000e4aa0(DAT_026d0438,local_178);
        }
        lVar15 = *(long *)(PTR_DAT_019b45d8 + 8);
        uVar6 = FUN_000e8680(lVar15,0,0xffffffff);
        thunk_FUN_012aa986(local_180,0,uVar6);
        uVar11 = *(ushort *)(lVar15 + 0x1c) & 0x78;
        bVar16 = uVar11 != 0;
        if (uVar11 == 0) {
          uVar3 = *(uint *)(lVar15 + 0x20);
          if ((*(ushort *)(lVar15 + 0x1c) & 0x40) != 0) {
            lVar7 = FUN_000e8a90(lVar15,local_180);
            if (lVar7 == 0) {
              uVar3 = uVar3 | 0x5488bf;
            }
            else {
              uVar3 = *(uint *)(lVar7 + 0x20) & 0x5488bf | uVar3;
            }
          }
          bVar16 = (uVar3 & 0xc08070) != 0;
        }
        if (bVar16) {
          FUN_000e6730(lVar15,local_180,0,0xffffffff,0);
        }
        local_180[0] = local_184;
        cVar2 = FUN_00b8f6c0(plVar1);
        if (cVar2 == '\0') {
          cVar2 = FUN_00b8f710(plVar1);
          if (cVar2 != '\0') {
            *(int *)(lVar10 + 0x5a0) = local_180[0];
            cVar2 = FUN_00b8f690(plVar1);
            if ((cVar2 == '\0') || (*(int *)(lVar10 + 0x59c) != *(int *)(lVar10 + 0x5a0))) {
              FUN_00b8f930(plVar1);
            }
          }
        }
        else {
          (**(code **)(*plVar1 + 0xa0))(plVar1,local_180);
        }
        goto LAB_007a9c25;
      }
      cVar2 = FUN_000e4d70(5,4);
      if (cVar2 == '\0') goto LAB_007a9c25;
      if ((DAT_026d0430 == '\0') && (iVar4 = thunk_FUN_012aa7d6(&DAT_026d0430), iVar4 != 0)) {
        DAT_026d0428 = FUN_000e4a10(s_world_controller_state_setup_act_0165d0b8);
        thunk_FUN_012aa7e6(&DAT_026d0430);
      }
      FUN_01008290(local_178,s_world_controller_state_setup_act_0165d0b8);
      uVar14 = DAT_026d0428;
    }
  }
  FUN_000e4aa0(uVar14,local_178);
LAB_007a9c25:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

