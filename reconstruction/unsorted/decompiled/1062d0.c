
void FUN_001062d0(void)

{
  short sVar1;
  long lVar2;
  long lVar3;
  undefined *puVar4;
  char cVar5;
  ushort uVar6;
  uint uVar7;
  int iVar8;
  ulong uVar9;
  undefined8 uVar10;
  long lVar11;
  ulong uVar12;
  long lVar13;
  undefined8 *puVar14;
  long lVar15;
  long lVar16;
  int iVar17;
  long lVar18;
  long local_138;
  long local_130;
  long local_120;
  undefined4 local_118;
  undefined1 local_110;
  undefined8 local_108;
  long lStack_100;
  undefined8 local_f8;
  uint local_f0;
  long local_e8;
  undefined4 local_e0;
  long local_d0;
  short local_c8;
  uint6 uStack_c6;
  char local_c0;
  undefined8 local_b8;
  undefined8 uStack_b0;
  undefined8 local_a8;
  undefined8 local_98;
  undefined8 uStack_90;
  undefined8 local_88;
  undefined8 local_78;
  undefined8 uStack_70;
  undefined8 local_68;
  undefined8 local_58;
  undefined8 uStack_50;
  undefined8 local_48;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_d0 = 0;
  uVar6 = FUN_00107550(0);
  local_d0 = 0;
  if (uVar6 != 0) {
    local_d0 = *(long *)(&DAT_01ad5030 + (ulong)uVar6 * DAT_01ad5010 + DAT_01ad5000);
  }
  local_c0 = '\0';
  FUN_0100c9b0(&local_d0);
  puVar4 = PTR_DAT_01975130;
  if (local_c0 != '\0') {
LAB_0010635a:
    local_b8 = 0;
    uStack_b0 = 0;
    local_a8 = 0;
    cVar5 = FUN_0100d0a0(&local_d0,0,&local_b8);
    if ((cVar5 != '\0') && ((int)local_b8 != -1)) {
      local_108 = 0;
      lStack_100 = 0;
      local_f8 = 0;
      cVar5 = FUN_0100d0a0(&local_d0,0,&local_108);
      if (cVar5 == '\0') {
        lVar15 = 0;
        uVar7 = 0xffffffff;
      }
      else {
        lVar15 = lStack_100;
        uVar7 = (uint)local_108;
      }
      lVar11 = (ulong)(((uint)((int)uVar7 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar7 >> 0xd) * 0x40;
      lVar16 = *DAT_01a238a0;
      lVar18 = *(long *)(lVar16 + 0x10 + lVar11);
      uVar9 = (ulong)((uVar7 & 0x1fff) * *(int *)(lVar16 + 0x30 + lVar11));
      lVar16 = (lVar18 + uVar9) -
               ((long)*(int *)(lVar16 + 0x34 + lVar11) & *(ulong *)(lVar18 + 8 + uVar9));
      if (0 < *(int *)(lVar15 + 0x278 + lVar16)) {
        lVar18 = lVar16 + 0x27c + lVar15;
        iVar17 = 0;
        do {
          iVar8 = FUN_00071f60(lVar18);
          lVar11 = DAT_025d79a8;
          if (iVar8 != -1) {
            uVar9 = (ulong)((*(uint *)(lVar18 + 4) & 0x1fff) * DAT_025d79b0);
            cVar5 = FUN_00337fe0((ulong)((*(uint *)(uVar9 + 0x3c + DAT_025d79a8) & 0x1fff) *
                                        DAT_02692230) + DAT_02692228,*(undefined4 *)puVar4,
                                 &local_108,0);
            if (cVar5 != '\0') {
              local_110 = 0;
              lVar2 = *DAT_01a238a0;
              lVar13 = (ulong)(((uint)((int)(uint)local_f8 >> 0xd) >> 0x12 | 0x3ff) &
                              (int)(uint)local_f8 >> 0xd) * 0x40;
              lVar3 = *(long *)(lVar2 + 0x10 + lVar13);
              uVar12 = (ulong)(((uint)local_f8 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar13));
              local_138 = (lVar3 + uVar12) -
                          ((long)*(int *)(lVar2 + 0x34 + lVar13) & *(ulong *)(lVar3 + 8 + uVar12));
              lVar13 = (ulong)(((uint)((int)local_f0 >> 0xd) >> 0x12 | 0x3ff) & (int)local_f0 >> 0xd
                              ) * 0x40;
              lVar3 = *(long *)(lVar2 + 0x10 + lVar13);
              uVar12 = (ulong)((local_f0 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar13));
              local_130 = ((lVar3 + uVar12) -
                          ((long)*(int *)(lVar2 + 0x34 + lVar13) & *(ulong *)(lVar3 + 8 + uVar12)))
                          + local_e8;
              local_118 = local_e0;
              local_120 = local_e8;
              FUN_00353610(&local_138);
            }
            puVar14 = (undefined8 *)(uVar9 + 0x28 + lVar11);
            puVar14[1] = 0;
            *puVar14 = 0;
            *(undefined4 *)puVar14 = 0xffffffff;
          }
          lVar18 = lVar18 + 8;
          iVar17 = iVar17 + 1;
        } while (iVar17 < *(int *)(lVar16 + 0x278 + lVar15));
      }
      do {
        local_c8 = local_c8 + 1;
        if (local_c8 < 0) {
          local_c0 = '\0';
          break;
        }
        if (uStack_c6 >> 0x10 == 0xffffffff) {
          sVar1 = *(short *)(local_d0 + 0x510);
        }
        else {
          sVar1 = *(short *)(local_d0 + 0x2bd1e + ((long)(int6)uStack_c6 >> 0x10) * 4);
        }
        local_c0 = local_c8 < sVar1;
        if (local_c8 < sVar1) {
          local_58 = 0;
          uStack_50 = 0;
          local_48 = 0;
          cVar5 = FUN_0100d0a0(&local_d0,0,&local_58);
          if ((cVar5 != '\0') && ((int)local_58 != -1)) goto LAB_00106658;
        }
        if (local_c0 == '\0') break;
      } while( true );
    }
  }
LAB_0010666d:
  FUN_0100c9b0(&local_d0);
  if (local_c0 == '\0') {
LAB_0010688e:
    if (*DAT_01a1f100 != local_38) {
      thunk_FUN_012aa7f6();
      return;
    }
    return;
  }
LAB_0010669a:
  local_78 = 0;
  uStack_70 = 0;
  local_68 = 0;
  cVar5 = FUN_0100d0a0(&local_d0,0,&local_78);
  if ((cVar5 != '\0') && ((int)local_78 != -1)) {
    local_108 = 0;
    lStack_100 = 0;
    local_f8 = 0;
    cVar5 = FUN_0100d0a0(&local_d0,0,&local_108);
    if (cVar5 == '\0') {
      lVar15 = 0;
      uVar7 = 0xffffffff;
    }
    else {
      lVar15 = lStack_100;
      uVar7 = (uint)local_108;
    }
    lVar11 = (ulong)(((uint)((int)uVar7 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar7 >> 0xd) * 0x40;
    lVar16 = *DAT_01a238a0;
    lVar18 = *(long *)(lVar16 + 0x10 + lVar11);
    uVar9 = (ulong)((uVar7 & 0x1fff) * *(int *)(lVar16 + 0x30 + lVar11));
    lVar16 = (lVar18 + uVar9) -
             ((long)*(int *)(lVar16 + 0x34 + lVar11) & *(ulong *)(lVar18 + 8 + uVar9));
    *(undefined4 *)(lVar15 + 0x278 + lVar16) = 0x28;
    uVar10 = FUN_00071fe0(0xffffffff);
    iVar17 = *(int *)(lVar15 + 0x278 + lVar16);
    if (0 < iVar17) {
      puVar14 = (undefined8 *)(lVar16 + 0x27c + lVar15);
      do {
        *puVar14 = uVar10;
        puVar14 = puVar14 + 1;
        iVar17 = iVar17 + -1;
      } while (iVar17 != 0);
    }
    *(undefined4 *)(lVar16 + 0x278 + lVar15) = 0;
    puVar14 = (undefined8 *)(lVar16 + 0x420 + lVar15);
    puVar14[1] = 0;
    *puVar14 = 0;
    *(undefined4 *)(lVar16 + 0x420 + lVar15) = 0xffffffff;
    *(undefined8 *)(lVar16 + 0x414 + lVar15) = 0;
    do {
      local_c8 = local_c8 + 1;
      if (local_c8 < 0) {
        local_c0 = '\0';
        break;
      }
      if (uStack_c6 >> 0x10 == 0xffffffff) {
        sVar1 = *(short *)(local_d0 + 0x510);
      }
      else {
        sVar1 = *(short *)(local_d0 + 0x2bd1e + ((long)(int6)uStack_c6 >> 0x10) * 4);
      }
      local_c0 = local_c8 < sVar1;
      if (local_c8 < sVar1) {
        local_98 = 0;
        uStack_90 = 0;
        local_88 = 0;
        cVar5 = FUN_0100d0a0(&local_d0,0,&local_98);
        if ((cVar5 != '\0') && ((int)local_98 != -1)) goto LAB_00106879;
      }
      if (local_c0 == '\0') break;
    } while( true );
  }
  goto LAB_0010688e;
LAB_00106658:
  if (local_c0 == '\0') goto LAB_0010666d;
  goto LAB_0010635a;
LAB_00106879:
  if (local_c0 == '\0') goto LAB_0010688e;
  goto LAB_0010669a;
}

