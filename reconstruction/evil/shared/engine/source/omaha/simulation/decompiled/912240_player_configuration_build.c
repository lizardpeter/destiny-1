
undefined8 FUN_00912240(ulong param_1,undefined4 *param_2)

{
  char *pcVar1;
  int *piVar2;
  short sVar3;
  int iVar4;
  long lVar5;
  undefined *puVar6;
  char cVar7;
  char cVar8;
  int iVar9;
  uint uVar10;
  int *piVar11;
  long *plVar12;
  undefined8 uVar13;
  undefined8 uVar14;
  long lVar15;
  long lVar16;
  int *piVar17;
  long lVar18;
  ulong uVar19;
  long lVar20;
  undefined4 *puVar21;
  int iVar22;
  float fVar23;
  undefined8 extraout_XMM0_Qa;
  undefined1 auVar24 [16];
  undefined1 extraout_var [56];
  long local_180;
  undefined4 local_178 [2];
  undefined4 local_170;
  undefined4 local_16c;
  undefined4 local_150 [2];
  int local_148 [2];
  int local_140 [2];
  int local_138 [64];
  long local_38;
  undefined1 auVar25 [64];
  
  local_38 = *DAT_01a1f100;
  lVar5 = *(long *)(DAT_0273ea80 + 8);
  cVar7 = FUN_0052b090();
  uVar13 = 0;
  if (cVar7 != '\0') {
    FUN_0066acc0(param_2);
    cVar7 = FUN_00549510();
    if ((cVar7 != '\0') &&
       (piVar11 = (int *)((param_1 & 0xffff) * 0x2af0),
       (*(byte *)(lVar5 + 0x613 + (long)piVar11) & 2) != 0)) {
      plVar12 = (long *)FUN_005753c0(4);
      local_180 = 0x7fffffffffffffff;
      if (plVar12 != (long *)0x0) {
        uVar13 = (**(code **)(*plVar12 + 0x18))(plVar12);
        uVar14 = (**(code **)(*plVar12 + 0x10))(plVar12);
        plVar12 = (long *)FUN_00265100(uVar13,uVar14);
        local_180 = *plVar12;
      }
      uVar13 = FUN_005494c0();
      lVar15 = FUN_0054b0c0(uVar13);
      pcVar1 = (char *)(lVar5 + 0x850 + (long)piVar11);
      plVar12 = (long *)FUN_0025cbd0();
      lVar16 = (**(code **)(*plVar12 + 0x68))(plVar12);
      piVar2 = (int *)(lVar5 + 0x85c + (long)piVar11);
      *param_2 = *(undefined4 *)(lVar5 + 0x85c + (long)piVar11);
      cVar7 = *(char *)(lVar5 + 0x852 + (long)piVar11);
      *(undefined1 *)(param_2 + 2) = 0;
      if (*(char *)(lVar16 + 0x13e) == cVar7) {
        *(undefined1 *)(param_2 + 2) = 0;
      }
      else if (*(char *)(lVar16 + 0x13d) == cVar7) {
        *(undefined1 *)(param_2 + 2) = 1;
      }
      else if (*(char *)(lVar16 + 0x13f) == cVar7) {
        *(undefined1 *)(param_2 + 2) = 2;
      }
      cVar7 = *(char *)(lVar5 + 0x851 + (long)piVar11);
      *(undefined1 *)((long)param_2 + 9) = 0;
      if (*(char *)(lVar16 + 0x13c) == cVar7) {
        *(undefined1 *)((long)param_2 + 9) = 0;
      }
      else if (*(char *)(lVar16 + 0x13b) == cVar7) {
        *(undefined1 *)((long)param_2 + 9) = 1;
      }
      cVar7 = *pcVar1;
      *(undefined1 *)((long)param_2 + 10) = 0;
      if (*(char *)(lVar16 + 0x138) == cVar7) {
        *(undefined1 *)((long)param_2 + 10) = 1;
      }
      else if (*(char *)(lVar16 + 0x139) == cVar7) {
        *(undefined1 *)((long)param_2 + 10) = 2;
      }
      else if (*(char *)(lVar16 + 0x13a) == cVar7) {
        *(undefined1 *)((long)param_2 + 10) = 3;
      }
      *(undefined1 *)((long)param_2 + 0xb) = *(undefined1 *)(lVar5 + 0x858 + (long)piVar11);
      FUN_00556a70(local_150,
                   *(undefined2 *)
                    ((long)piVar11 + (long)*(char *)(lVar15 + 10) * 0x40 + 0xe48 + lVar5));
      param_2[1] = local_150[0];
      FUN_00910e40(pcVar1,param_2 + 0x60);
      FUN_009110d0(pcVar1,param_2 + 200);
      FUN_009101f0((long)piVar11 + (long)*(char *)(lVar15 + 0x15) * 0x40 + 0xe40 + lVar5);
      FUN_00910380((long)piVar11 + (long)*(char *)(lVar15 + 0x14) * 0x40 + 0xe40 + lVar5,
                   (long)piVar11 + (long)*(char *)(lVar15 + 0x14) * 0x20 + 0x9c8 + lVar5,
                   param_2 + 0xcc);
      if ((long)*(char *)(lVar15 + 0x17) != -1) {
        FUN_009106f0((long)piVar11 + (long)*(char *)(lVar15 + 0x16) * 0x40 + 0xe40 + lVar5,
                     (long)piVar11 + (long)*(char *)(lVar15 + 0x17) * 0x40 + 0xe40 + lVar5,
                     param_2 + 0xd6);
      }
      cVar7 = *(char *)(lVar15 + 0x11);
      FUN_00910c60(cVar7,(long)piVar11 + (long)cVar7 * 0x40 + 0xe40 + lVar5,
                   (long)piVar11 + (long)cVar7 * 0x20 + 0x9c8 + lVar5,lVar5 + 0x1400 + (long)piVar11
                   ,&DAT_000014e0 + lVar5 + (long)piVar11,param_2 + 0xda);
      cVar7 = *(char *)(lVar15 + 0x12);
      FUN_00910c60(cVar7,(long)piVar11 + (long)cVar7 * 0x40 + 0xe40 + lVar5,
                   (long)piVar11 + (long)cVar7 * 0x20 + 0x9c8 + lVar5,lVar5 + 0x1420 + (long)piVar11
                   ,lVar5 + 0x1560 + (long)piVar11,param_2 + 0x1a2);
      cVar7 = *(char *)(lVar15 + 0x13);
      FUN_00910c60(cVar7,(long)piVar11 + (long)cVar7 * 0x40 + 0xe40 + lVar5,
                   (long)piVar11 + (long)cVar7 * 0x20 + 0x9c8 + lVar5,lVar5 + 0x1440 + (long)piVar11
                   ,lVar5 + 0x15e0 + (long)piVar11,param_2 + 0x26a);
      lVar15 = lVar5 + 0xdbc + (long)piVar11;
      FUN_0090fc90(lVar15,lVar5 + 0xc68 + (long)piVar11,param_2 + 0x332);
      FUN_0090fc90(lVar15,lVar5 + 0xcac + (long)piVar11,param_2 + 0x355);
      FUN_0090fc90(lVar15,lVar5 + 0xcf0 + (long)piVar11,param_2 + 0x378);
      FUN_0090fc90(lVar15,lVar5 + 0xd34 + (long)piVar11,param_2 + 0x39b);
      FUN_0090fc90(lVar15,lVar5 + 0xd78 + (long)piVar11,param_2 + 0x3be);
      lVar15 = 0;
      iVar22 = 0;
      piVar17 = piVar11;
      do {
        sVar3 = *(short *)((param_1 & 0xffff) * 0x2af0 + 0x13c0 + lVar5 + lVar15 * 2);
        piVar17 = (int *)CONCAT62((int6)((ulong)piVar17 >> 0x10),sVar3);
        uVar13 = FUN_005494c0();
        if (sVar3 != -1) {
          piVar17 = (int *)FUN_0054c9b0(uVar13,(ulong)piVar17 & 0xffffffff);
          if ((piVar17 != (int *)0x0) && (*piVar17 != -0x7ee3623b)) {
            uVar13 = FUN_0033fa20();
            local_140[0] = *piVar17;
            iVar9 = FUN_0033fc20(uVar13,local_140);
            if ((iVar9 != -1) && (iVar22 < 0x1f)) {
              param_2[(long)iVar22 + 0x404] = iVar9;
              iVar22 = iVar22 + 1;
            }
          }
        }
        lVar15 = lVar15 + 1;
      } while ((int)lVar15 != 0x20);
      lVar15 = lVar5 + (param_1 & 0xffff) * 0x2af0;
      lVar16 = 0;
      do {
        if (((&DAT_00001348)[lVar16 + lVar15 + -8] != -1) &&
           (local_180 < *(long *)(&DAT_00001348 + lVar16 + lVar15))) {
          plVar12 = (long *)FUN_0025cbd0();
          lVar18 = (**(code **)(*plVar12 + 0xa8))(plVar12);
          sVar3 = *(short *)(lVar18 + *(long *)(lVar18 + 8) + 0x1c +
                            (long)(char)(&DAT_00001348)[lVar16 + lVar15 + -8] * 8);
          piVar17 = (int *)CONCAT62((int6)((ulong)piVar17 >> 0x10),sVar3);
          uVar13 = FUN_005494c0();
          if (sVar3 != -1) {
            piVar17 = (int *)FUN_0054c9b0(uVar13,(ulong)piVar17 & 0xffffffff);
            if ((piVar17 != (int *)0x0) && (*piVar17 != -0x7ee3623b)) {
              uVar13 = FUN_0033fa20();
              local_148[0] = *piVar17;
              iVar9 = FUN_0033fc20(uVar13,local_148);
              if ((iVar9 != -1) && (iVar22 < 0x1f)) {
                param_2[(long)iVar22 + 0x404] = iVar9;
                iVar22 = iVar22 + 1;
              }
            }
          }
        }
        lVar16 = lVar16 + 0x10;
      } while ((int)lVar16 != 0x80);
      FUN_00546fd0(lVar5 + 0xc58 + (long)piVar11,param_2 + 3);
      if (*piVar2 != -1) {
        lVar15 = FUN_005753c0(4);
        uVar13 = FUN_003369c0(*piVar2);
        puVar6 = PTR_DAT_019b3270;
        uVar10 = FUN_00336cc0(uVar13,*(undefined4 *)PTR_DAT_019b3270);
        if ((uVar10 != 0xffffffff) && (lVar15 != 0)) {
          iVar22 = FUN_002668a0(lVar15);
          if (iVar22 != -1) {
            lVar18 = (ulong)(((uint)((int)uVar10 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar10 >> 0xd) *
                     0x40;
            lVar15 = *DAT_01a238a0;
            local_180 = 0;
            lVar16 = *(long *)(lVar15 + 0x10 + lVar18);
            uVar19 = (ulong)((uVar10 & 0x1fff) * *(int *)(lVar15 + 0x30 + lVar18));
            lVar16 = (lVar16 + uVar19) -
                     ((long)*(int *)(lVar15 + 0x34 + lVar18) & *(ulong *)(lVar16 + 8 + uVar19));
            if (*(long *)(lVar16 + 0x18) != 0) {
              uVar10 = *(uint *)(lVar16 + 0x14 + *(long *)(lVar16 + 0x18));
              local_180 = 0;
              lVar18 = 0;
              if (uVar10 != 0xffffffff) {
                lVar20 = (ulong)(((uint)((int)uVar10 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar10 >> 0xd)
                         * 0x40;
                lVar18 = *(long *)(lVar15 + 0x10 + lVar20);
                uVar19 = (ulong)((uVar10 & 0x1fff) * *(int *)(lVar15 + 0x30 + lVar20));
                lVar18 = (lVar18 + uVar19) -
                         ((long)*(int *)(lVar15 + 0x34 + lVar20) & *(ulong *)(lVar18 + 8 + uVar19));
              }
              cVar7 = FUN_000e8020(lVar18,*(undefined8 *)(puVar6 + 8));
              if ((cVar7 != '\0') && (lVar15 = *(long *)(lVar16 + 0x18), lVar15 != 0)) {
                local_180 = lVar15 + lVar16 + 0x18;
              }
            }
            FUN_0028a2f0(lVar5 + 0x1460 + (long)piVar11,local_138);
            puVar21 = param_2 + 8;
            iVar9 = 0;
            do {
              cVar7 = FUN_005dd050(local_180,iVar9,param_2,&local_170);
              if (cVar7 != '\0') {
                cVar7 = FUN_00553580(iVar9);
                if (cVar7 != -1) {
                  iVar4 = local_138[cVar7];
                  if (DAT_018fb6a8 == '\0') {
LAB_00912948:
                    uVar13 = FUN_00281c40(cVar7,iVar4,iVar22);
                    uVar13 = FUN_000915e0(local_170,local_16c,uVar13);
                  }
                  else {
                    cVar8 = FUN_00281ba0(cVar7);
                    auVar25._8_56_ = extraout_var;
                    auVar25._0_8_ = extraout_XMM0_Qa;
                    if (cVar8 != '\0') goto LAB_00912948;
                    auVar24._0_4_ = (float)iVar4;
                    auVar24._4_12_ = auVar25._4_12_;
                    uVar13 = auVar24._0_8_;
                  }
                  FUN_00673800(uVar13,puVar21);
                }
              }
              puVar21 = puVar21 + 8;
              iVar9 = iVar9 + 1;
            } while (iVar9 != 6);
          }
        }
      }
      iVar22 = FUN_0052b950();
      if (iVar22 != -1) {
        param_2[0x3e1] = iVar22;
      }
    }
    lVar16 = (param_1 & 0xffff) * 0x2af0;
    param_2[0xdb] = *(undefined4 *)(lVar5 + 0x19cc + lVar16);
    local_178[0] = DAT_025d7310;
    FUN_00118870(local_178);
    FUN_00672a50(param_2 + 0xda);
    puVar6 = PTR_DAT_01996020;
    param_2[0x1a3] = *(undefined4 *)(lVar5 + 0x1cec + lVar16);
    local_178[0] = DAT_025d7310;
    lVar15 = FUN_00118870(local_178);
    if ((((lVar15 != 0) && (*(int *)(lVar15 + 4) == *(int *)puVar6)) &&
        (*(char *)(lVar15 + 8) != '\0')) &&
       (*(long *)(lVar5 + 0x1d00 + lVar16) != *(long *)(param_2 + 0x1a8))) {
      fVar23 = (float)FUN_00668ba0();
      param_2[0x1a3] = fVar23 * (float)param_2[0x1a3];
    }
    FUN_00672a50(param_2 + 0x1a2);
    param_2[0x26b] = *(undefined4 *)(lVar5 + 0x200c + lVar16);
    local_178[0] = DAT_025d7310;
    lVar15 = FUN_00118870(local_178);
    if (((lVar15 != 0) && (*(int *)(lVar15 + 4) == *(int *)puVar6)) &&
       ((*(char *)(lVar15 + 8) != '\0' &&
        (*(long *)(lVar5 + 0x2020 + lVar16) != *(long *)(param_2 + 0x270))))) {
      fVar23 = (float)FUN_00668ba0();
      param_2[0x26b] = fVar23 * (float)param_2[0x26b];
    }
    FUN_00672a50(param_2 + 0x26a);
    uVar13 = 1;
  }
  if (*DAT_01a1f100 == local_38) {
    return uVar13;
  }
  uVar13 = thunk_FUN_012aa7f6();
  return uVar13;
}

