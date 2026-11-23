
void FUN_00773380(void)

{
  long *plVar1;
  int iVar2;
  uint uVar3;
  byte bVar4;
  char cVar5;
  char cVar6;
  int iVar7;
  int iVar8;
  char *pcVar9;
  int iVar10;
  int iVar11;
  long *plVar12;
  int iVar13;
  long lVar14;
  byte bVar15;
  long lVar16;
  long *plVar17;
  long *plVar18;
  long lVar19;
  long lVar20;
  long *plVar21;
  long lVar22;
  long lVar23;
  long *plVar24;
  char *pcVar25;
  long *plVar26;
  bool bVar27;
  bool bVar28;
  undefined4 local_68;
  undefined2 local_64;
  char local_62;
  undefined4 local_60;
  undefined2 local_5c;
  char local_5a;
  undefined4 local_58;
  undefined2 local_54;
  char local_52;
  undefined4 local_50;
  undefined2 local_4c;
  char local_4a;
  undefined4 local_48;
  undefined2 local_44;
  char local_42;
  undefined4 local_40;
  undefined2 local_3c;
  char local_3a;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  pcVar9 = (char *)0x0;
  if ((DAT_026ca4e0 != (char *)0x0) && (pcVar9 = (char *)0x0, *DAT_026ca4e0 != '\0')) {
    pcVar9 = DAT_026ca4e0;
  }
  if (*pcVar9 == '\0') goto LAB_00773cb5;
  lVar22 = (long)*(int *)(pcVar9 + 0x26398) * 0x98e0;
  lVar19 = (long)*(int *)(pcVar9 + 0x131d0) * 0x98e0;
  lVar20 = (long)*(int *)(pcVar9 + 8) * 0x98e0;
  lVar14 = ((long)*(int *)(pcVar9 + 0x26398) ^ 1U) * 0x98e0;
  lVar16 = ((long)*(int *)(pcVar9 + 0x131d0) ^ 1U) * 0x98e0;
  iVar8 = *(int *)(pcVar9 + lVar16 + 0x1be20);
  iVar11 = *(int *)(pcVar9 + lVar14 + 0x2efe8);
  iVar13 = *(int *)(pcVar9 + lVar20 + 0x8c58);
  iVar2 = *(int *)(pcVar9 + lVar19 + 0x1be20);
  iVar10 = *(int *)(pcVar9 + lVar22 + 0x2efe8);
  lVar23 = ((long)*(int *)(pcVar9 + 8) ^ 1U) * 0x98e0;
  plVar12 = (long *)0x0;
  plVar18 = (long *)(pcVar9 + lVar22 + 0x263a0);
  if (iVar10 == 0) {
    plVar18 = plVar12;
  }
  plVar21 = (long *)(pcVar9 + lVar19 + 0x131d8);
  if (iVar2 == 0) {
    plVar21 = plVar12;
  }
  plVar17 = (long *)(pcVar9 + lVar20 + 0x10);
  if (iVar13 == 0) {
    plVar17 = plVar12;
  }
  plVar24 = (long *)(pcVar9 + lVar14 + 0x263a0);
  if (iVar11 == 0) {
    plVar24 = plVar12;
  }
  plVar26 = (long *)(pcVar9 + lVar16 + 0x131d8);
  if (iVar8 == 0) {
    plVar26 = plVar12;
  }
  plVar12 = (long *)(pcVar9 + lVar23 + 0x10);
  if ((*(int *)(pcVar9 + lVar23 + 0x8c58) != 0) &&
     (((uVar3 = *(uint *)(plVar12 + 0x1189), (uVar3 & 0xfffffffe) == 6 || (uVar3 == 8)) ||
      (uVar3 == 9)))) {
    local_3a = '\0';
    local_3c = 0;
    local_40 = 0;
    bVar4 = (**(code **)(*plVar12 + 0x28))(plVar12);
    local_40._0_2_ = (ushort)bVar4;
    plVar1 = plVar12 + 0xd85;
    cVar5 = FUN_00b8f6c0(plVar1);
    if (cVar5 != '\0') {
      iVar7 = thunk_FUN_012aa826((char *)((long)plVar12 + 0x6d09),&local_40,7);
      if ((iVar7 != 0) || (cVar5 = FUN_00b8f690(plVar1), cVar5 == '\0')) {
        *(char *)((long)plVar12 + 0x6d0f) = local_3a;
        *(undefined2 *)((long)plVar12 + 0x6d0d) = local_3c;
        *(undefined4 *)((long)plVar12 + 0x6d09) = local_40;
        FUN_00b8f880(plVar1);
      }
    }
  }
  if ((iVar8 != 0) &&
     (((uVar3 = *(uint *)(plVar26 + 0x1189), (uVar3 & 0xfffffffe) == 6 || (uVar3 == 8)) ||
      (uVar3 == 9)))) {
    local_42 = '\0';
    local_44 = 0;
    local_48 = 0;
    bVar4 = (**(code **)(*plVar26 + 0x28))(plVar26);
    local_48._0_2_ = (ushort)bVar4;
    plVar12 = plVar26 + 0xd85;
    cVar5 = FUN_00b8f6c0(plVar12);
    if (cVar5 != '\0') {
      iVar8 = thunk_FUN_012aa826((char *)((long)plVar26 + 0x6d09),&local_48,7);
      if ((iVar8 != 0) || (cVar5 = FUN_00b8f690(plVar12), cVar5 == '\0')) {
        *(char *)((long)plVar26 + 0x6d0f) = local_42;
        *(undefined2 *)((long)plVar26 + 0x6d0d) = local_44;
        *(undefined4 *)((long)plVar26 + 0x6d09) = local_48;
        FUN_00b8f880(plVar12);
      }
    }
  }
  if ((iVar10 != 0) &&
     (((uVar3 = *(uint *)(plVar18 + 0x1189), (uVar3 & 0xfffffffe) == 6 || (uVar3 == 8)) ||
      (uVar3 == 9)))) {
    cVar5 = FUN_00b8f690(plVar18 + 0xf00);
    if (cVar5 != '\0') {
      cVar5 = FUN_00b8f690(plVar18 + 0xf00);
      pcVar9 = (char *)0x0;
      if (cVar5 != '\0') {
        pcVar9 = (char *)((long)plVar18 + 0x78e1);
      }
      local_50 = 0x1141400;
      local_4c = 0;
      local_4a = 0;
      iVar8 = (**(code **)(*plVar18 + 0x28))(plVar18);
      cVar5 = *pcVar9;
      local_50 = CONCAT31(local_50._1_3_,cVar5);
      bVar4 = pcVar9[2];
      local_4c = CONCAT11(bVar4,(undefined1)local_4c);
      lVar14 = FUN_00574ef0();
      bVar15 = bVar4;
      if (*(char *)(lVar14 + 300) != '\0') {
        bVar15 = bVar4 | 4;
        local_4c = CONCAT11(bVar4,(undefined1)local_4c) | 0x400;
      }
      bVar27 = (bVar15 & 0x1f) != 0;
      if (bVar27) {
        local_50 = local_50 & 0xffffff;
      }
      local_4a = pcVar9[1];
      if (((pcVar9[2] & 8U) != 0) || (pcVar9[3] != '\0')) {
        local_4a = '\0';
      }
      bVar4 = 0x14;
      if (bVar27 && local_4a == '\0') {
        local_50._0_2_ = (ushort)(byte)local_50;
        bVar4 = 0;
      }
      iVar10 = cVar5 - iVar8;
      if ((int)(uint)bVar4 < iVar10) {
        local_50 = CONCAT31(local_50._1_3_,(char)((uint)bVar4 + iVar8));
      }
      else if ((int)cVar5 < (int)((uint)bVar4 + iVar8)) {
        bVar4 = (byte)iVar10;
        local_50._0_2_ = CONCAT11(bVar4,(byte)local_50);
      }
      if (bVar4 == 0) {
        local_50 = local_50 & 0xffffff;
        local_4a = '\0';
      }
      plVar12 = plVar18 + 0xd85;
      cVar5 = FUN_00b8f6c0(plVar12);
      if (cVar5 != '\0') {
        iVar8 = thunk_FUN_012aa826((uint *)((long)plVar18 + 0x6d09),&local_50,7);
        if ((iVar8 != 0) || (cVar5 = FUN_00b8f690(plVar12), cVar5 == '\0')) {
          *(char *)((long)plVar18 + 0x6d0f) = local_4a;
          *(ushort *)((long)plVar18 + 0x6d0d) = local_4c;
          *(uint *)((long)plVar18 + 0x6d09) = local_50;
          FUN_00b8f880(plVar12);
        }
      }
    }
  }
  if ((iVar11 != 0) &&
     (((uVar3 = *(uint *)(plVar24 + 0x1189), (uVar3 & 0xfffffffe) == 6 || (uVar3 == 8)) ||
      (uVar3 == 9)))) {
    cVar5 = FUN_00b8f690(plVar24 + 0xf00);
    if (cVar5 != '\0') {
      cVar5 = FUN_00b8f690(plVar24 + 0xf00);
      pcVar9 = (char *)0x0;
      if (cVar5 != '\0') {
        pcVar9 = (char *)((long)plVar24 + 0x78e1);
      }
      local_58 = 0x1141400;
      local_54 = 0;
      local_52 = 0;
      iVar8 = (**(code **)(*plVar24 + 0x28))(plVar24);
      cVar5 = *pcVar9;
      local_58 = CONCAT31(local_58._1_3_,cVar5);
      bVar4 = pcVar9[2];
      local_54 = CONCAT11(bVar4,(undefined1)local_54);
      lVar14 = FUN_00574ef0();
      bVar15 = bVar4;
      if (*(char *)(lVar14 + 300) != '\0') {
        bVar15 = bVar4 | 4;
        local_54 = CONCAT11(bVar4,(undefined1)local_54) | 0x400;
      }
      bVar27 = (bVar15 & 0x1f) != 0;
      if (bVar27) {
        local_58 = local_58 & 0xffffff;
      }
      local_52 = pcVar9[1];
      if (((pcVar9[2] & 8U) != 0) || (pcVar9[3] != '\0')) {
        local_52 = '\0';
      }
      bVar4 = 0x14;
      if (bVar27 && local_52 == '\0') {
        local_58._0_2_ = (ushort)(byte)local_58;
        bVar4 = 0;
      }
      iVar11 = cVar5 - iVar8;
      if ((int)(uint)bVar4 < iVar11) {
        local_58 = CONCAT31(local_58._1_3_,(char)((uint)bVar4 + iVar8));
      }
      else if ((int)cVar5 < (int)((uint)bVar4 + iVar8)) {
        bVar4 = (byte)iVar11;
        local_58._0_2_ = CONCAT11(bVar4,(byte)local_58);
      }
      if (bVar4 == 0) {
        local_58 = local_58 & 0xffffff;
        local_52 = '\0';
      }
      plVar18 = plVar24 + 0xd85;
      cVar5 = FUN_00b8f6c0(plVar18);
      if (cVar5 != '\0') {
        iVar8 = thunk_FUN_012aa826((uint *)((long)plVar24 + 0x6d09),&local_58,7);
        if ((iVar8 != 0) || (cVar5 = FUN_00b8f690(plVar18), cVar5 == '\0')) {
          *(char *)((long)plVar24 + 0x6d0f) = local_52;
          *(ushort *)((long)plVar24 + 0x6d0d) = local_54;
          *(uint *)((long)plVar24 + 0x6d09) = local_58;
          FUN_00b8f880(plVar18);
        }
      }
    }
  }
  if (iVar13 == 0) goto LAB_00773cb5;
  uVar3 = *(uint *)(plVar17 + 0x1189);
  if ((((uVar3 & 0xfffffffe) == 6) || (uVar3 == 8)) || (uVar3 == 9)) {
    if (iVar2 != 0) goto LAB_0077392a;
    bVar27 = true;
    plVar18 = (long *)0x0;
  }
  else {
    if ((iVar2 == 0) ||
       (((uVar3 = *(uint *)(plVar21 + 0x1189), (uVar3 & 0xfffffffe) != 6 && (uVar3 != 8)) &&
        (uVar3 != 9)))) goto LAB_00773cb5;
LAB_0077392a:
    plVar18 = plVar21 + 0xd65;
    bVar27 = false;
  }
  cVar5 = FUN_00b8f690(plVar17 + 0xf00);
  if ((cVar5 != '\0') &&
     ((plVar18 == (long *)0x0 || (cVar5 = FUN_00b8f690(plVar18 + 0x19b), cVar5 != '\0')))) {
    local_5c = local_5c & 0xff;
    local_68 = 0x1141414;
    local_64 = 0;
    local_62 = '\0';
    iVar8 = 0x14;
    if (plVar18 != (long *)0x0) {
      cVar5 = FUN_00b8f690(plVar18 + 0x19b);
      pcVar9 = (char *)0x0;
      if (cVar5 != '\0') {
        pcVar9 = (char *)((long)plVar18 + 0xdb9);
      }
      iVar8 = (**(code **)(*plVar21 + 0x28))();
      cVar5 = *pcVar9;
      local_68 = CONCAT31(local_68._1_3_,cVar5);
      bVar4 = pcVar9[2];
      local_64 = CONCAT11(bVar4,(undefined1)local_64);
      lVar14 = FUN_00574ef0();
      bVar15 = bVar4;
      if (*(char *)(lVar14 + 300) != '\0') {
        bVar15 = bVar4 | 4;
        local_64 = CONCAT11(bVar4,(undefined1)local_64) | 0x400;
      }
      bVar28 = (bVar15 & 0x1f) != 0;
      if (bVar28) {
        local_68 = local_68 & 0xffffff;
      }
      local_62 = pcVar9[1];
      if (((pcVar9[2] & 8U) != 0) || (pcVar9[3] != '\0')) {
        local_62 = '\0';
      }
      bVar4 = 0x14;
      if (bVar28 && local_62 == '\0') {
        local_68._0_2_ = (ushort)(byte)local_68;
        bVar4 = 0;
      }
      iVar11 = cVar5 - iVar8;
      if ((int)(uint)bVar4 < iVar11) {
        local_68 = CONCAT31(local_68._1_3_,(char)((uint)bVar4 + iVar8));
      }
      else if ((int)cVar5 < (int)((uint)bVar4 + iVar8)) {
        bVar4 = (byte)iVar11;
        local_68._0_2_ = CONCAT11(bVar4,(byte)local_68);
      }
      if (bVar4 == 0) {
        local_68 = local_68 & 0xffffff;
        local_62 = '\0';
      }
      iVar8 = 0x14;
      if (*pcVar9 < 0x15) {
        iVar8 = (int)*pcVar9;
      }
    }
    local_5a = local_62;
    local_5c = local_64;
    local_60 = local_68;
    cVar5 = FUN_00b8f690(plVar17 + 0xf00);
    pcVar9 = (char *)((long)plVar17 + 0x78e1);
    if (cVar5 == '\0') {
      pcVar9 = (char *)0x0;
    }
    cVar5 = FUN_00b8f690(plVar17 + 0xee3);
    pcVar25 = (char *)0x0;
    if (cVar5 != '\0') {
      cVar5 = FUN_00b8f690(plVar17 + 0xee3);
      pcVar25 = (char *)0x0;
      if (cVar5 != '\0') {
        pcVar25 = (char *)((long)plVar17 + 0x77f9);
      }
    }
    iVar11 = (**(code **)(*plVar17 + 0x28))();
    if ((pcVar25 != (char *)0x0) && (pcVar25[1] != '\0')) {
      local_60 = local_60 & 0xffffff;
      local_5a = '\0';
    }
    cVar5 = *pcVar9;
    local_60 = CONCAT31(local_60._1_3_,cVar5);
    bVar4 = pcVar9[2];
    local_5c = CONCAT11(bVar4,(undefined1)local_5c);
    lVar14 = FUN_00574ef0();
    bVar15 = bVar4;
    if (*(char *)(lVar14 + 300) != '\0') {
      bVar15 = bVar4 | 4;
      local_5c = CONCAT11(bVar4,(undefined1)local_5c) | 0x400;
    }
    if ((bVar15 & 0x1f) != 0) {
      local_60 = local_60 & 0xffffff;
    }
    local_5a = pcVar9[1];
    if (((pcVar9[2] & 8U) != 0) || (pcVar9[3] != '\0')) {
      local_5a = '\0';
    }
    if (local_5a == '\0' && local_60._3_1_ == '\0') {
      local_60._0_2_ = (ushort)(byte)local_60;
      cVar6 = '\0';
    }
    else {
      cVar6 = local_60._1_1_;
    }
    iVar13 = cVar6 + iVar11;
    iVar11 = cVar5 - iVar11;
    if (cVar6 < iVar11) {
      local_60 = CONCAT31(local_60._1_3_,(char)iVar13);
    }
    else if (cVar5 < iVar13) {
      cVar6 = (char)iVar11;
      local_60._0_2_ = CONCAT11(cVar6,(byte)local_60);
    }
    if (cVar6 == '\0') {
      local_60 = local_60 & 0xffffff;
      local_5a = '\0';
    }
    if ((pcVar25 != (char *)0x0) && (pcVar25[1] != '\0')) {
      iVar8 = 0;
    }
    if ((pcVar9[2] & 0x1fU) != 0) {
      iVar8 = 0;
    }
    if (*pcVar9 <= iVar8) {
      iVar8 = (int)*pcVar9;
    }
    iVar13 = (**(code **)(*plVar17 + 0x28))(plVar17);
    iVar11 = iVar8 - iVar13;
    if (iVar8 - iVar13 < 0) {
      iVar11 = 0;
    }
    local_60._0_3_ = CONCAT12((char)iVar11,(ushort)local_60);
    local_5c = CONCAT11(local_5c._1_1_,iVar11 != 0);
    uVar3 = *(uint *)(plVar17 + 0x1189);
    if ((((uVar3 & 0xfffffffe) == 6) || (uVar3 == 8)) || (uVar3 == 9)) {
      plVar12 = plVar17 + 0xd85;
      cVar5 = FUN_00b8f6c0(plVar12);
      if (cVar5 != '\0') {
        iVar8 = thunk_FUN_012aa826((char *)((long)plVar17 + 0x6d09),&local_60,7);
        if ((iVar8 != 0) || (cVar5 = FUN_00b8f690(plVar12), cVar5 == '\0')) {
          *(char *)((long)plVar17 + 0x6d0f) = local_5a;
          *(ushort *)((long)plVar17 + 0x6d0d) = local_5c;
          *(uint *)((long)plVar17 + 0x6d09) = local_60;
          FUN_00b8f880(plVar12);
        }
      }
    }
    if ((!bVar27) &&
       (((uVar3 = *(uint *)(plVar21 + 0x1189), (uVar3 & 0xfffffffe) == 6 || (uVar3 == 8)) ||
        (uVar3 == 9)))) {
      plVar12 = plVar18 + 0x20;
      cVar5 = FUN_00b8f6c0(plVar12);
      if (cVar5 != '\0') {
        iVar8 = thunk_FUN_012aa826((uint *)((long)plVar18 + 0x1e1),&local_68,7);
        if ((iVar8 != 0) || (cVar5 = FUN_00b8f690(plVar12), cVar5 == '\0')) {
          *(char *)((long)plVar18 + 0x1e7) = local_62;
          *(ushort *)((long)plVar18 + 0x1e5) = local_64;
          *(uint *)((long)plVar18 + 0x1e1) = local_68;
          FUN_00b8f880(plVar12);
        }
      }
    }
  }
LAB_00773cb5:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

