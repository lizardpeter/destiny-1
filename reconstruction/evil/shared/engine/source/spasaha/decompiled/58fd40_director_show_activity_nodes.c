
void FUN_0058fd40(long param_1,undefined8 param_2)

{
  long *plVar1;
  undefined1 *puVar2;
  uint *puVar3;
  byte bVar4;
  undefined *puVar5;
  char cVar6;
  undefined1 uVar7;
  char cVar8;
  undefined1 uVar9;
  short sVar10;
  long lVar11;
  long *plVar12;
  undefined8 uVar13;
  long lVar14;
  int *piVar15;
  short *psVar16;
  ushort uVar17;
  int iVar18;
  uint uVar19;
  long lVar20;
  long lVar21;
  long lVar22;
  long lVar23;
  bool bVar24;
  undefined1 auVar25 [16];
  uint auStack_11a0 [766];
  undefined1 local_5a8 [24];
  long local_590;
  undefined8 local_588;
  long local_580;
  char local_56f;
  long local_568;
  long local_560;
  undefined8 local_558 [3];
  long local_540;
  undefined1 local_538 [24];
  undefined1 local_520 [24];
  undefined4 local_508 [2];
  long local_500;
  int local_4f8;
  short sStack_4f4;
  undefined1 auStack_4f2 [82];
  undefined8 local_4a0 [32];
  undefined1 local_3a0 [256];
  undefined1 local_2a0 [256];
  uint local_1a0 [68];
  undefined1 local_90 [16];
  int local_80 [8];
  long local_60;
  
  local_60 = *DAT_01a1f100;
  local_500 = FUN_00587520();
  local_4a0[0] = 0;
  if ((local_500 != 0) && (lVar11 = FUN_002601f0(param_2), *(char *)(lVar11 + 1) != '\0')) {
    plVar12 = (long *)FUN_0025a550();
    thunk_FUN_012aa986(param_1 + 0x18e0,0,0x2200);
    puVar5 = PTR_DAT_019e4dc0;
    lVar11 = 0;
    do {
      if (DAT_0295d371 == '\0') {
        lVar23 = *(long *)(puVar5 + 8);
        uVar13 = FUN_000e8680(lVar23,0,0xffffffff);
        thunk_FUN_012aa986(local_4a0,0,uVar13);
        uVar17 = *(ushort *)(lVar23 + 0x1c) & 0x78;
        bVar24 = uVar17 != 0;
        if (uVar17 == 0) {
          uVar19 = *(uint *)(lVar23 + 0x20);
          if ((*(ushort *)(lVar23 + 0x1c) & 0x40) != 0) {
            lVar14 = FUN_000e8a90(lVar23);
            if (lVar14 == 0) {
              uVar19 = uVar19 | 0x5488bf;
            }
            else {
              uVar19 = *(uint *)(lVar14 + 0x20) & 0x5488bf | uVar19;
            }
          }
          bVar24 = (uVar19 & 0xc08070) != 0;
        }
        if (bVar24) {
          FUN_000e6730(lVar23,local_4a0,0,0xffffffff,0);
        }
        DAT_0295d372 = (undefined1)local_4a0[0];
        DAT_0295d371 = '\x01';
      }
      *(undefined1 *)(param_1 + 0x3ae0 + lVar11) = DAT_0295d372;
      lVar11 = lVar11 + 1;
    } while ((int)lVar11 != 0x800);
    local_80[0] = 0;
    local_80[1] = 0;
    local_80[2] = 0;
    local_80[3] = 0;
    local_80[4] = 0;
    local_80[5] = 0;
    local_80[6] = 0;
    local_80[7] = 0;
    local_508[0] = 10;
    FUN_0057f860(local_90,&local_500,local_508);
    uVar13 = FUN_00582a40();
    FUN_0057f880(local_90);
    cVar6 = FUN_001d1b20(local_90);
    if (cVar6 != '\0') {
      bVar24 = false;
      do {
        FUN_0057f9b0(local_90,local_4a0);
        lVar11 = FUN_00580840(uVar13,local_4a0);
        if ((lVar11 != 0) && (*(short *)(lVar11 + 10) != -1)) {
          cVar6 = FUN_00545280();
          piVar15 = (int *)(param_1 + 0x1ae0 + (long)*(short *)(lVar11 + 10) * 4);
          *piVar15 = *piVar15 + 1;
          if (cVar6 != -1) {
            local_80[cVar6] = local_80[cVar6] + 1;
            bVar24 = true;
          }
        }
        FUN_0057f920(local_90);
        cVar6 = FUN_001d1b20(local_90);
      } while (cVar6 != '\0');
      if (bVar24) {
        lVar11 = 0;
        do {
          iVar18 = local_80[lVar11];
          if (0 < iVar18) {
            lVar14 = (**(code **)(*plVar12 + 0x458))();
            lVar23 = *(long *)(lVar14 + 8);
            if (0 < lVar23) {
              lVar21 = 0;
              lVar22 = 0x14;
              do {
                lVar20 = (long)*(short *)(lVar14 + 0x10 + lVar22 + *(long *)(lVar14 + 0x10));
                if (lVar20 != -1) {
                  *(int *)(param_1 + 0x1ae0 + lVar20 * 4) = iVar18;
                  lVar23 = *(long *)(lVar14 + 8);
                }
                lVar22 = lVar22 + 0x28;
                lVar21 = lVar21 + 1;
              } while (lVar21 < lVar23);
            }
          }
          lVar11 = lVar11 + 1;
        } while ((char)lVar11 != '\b');
      }
    }
    piVar15 = (int *)(**(code **)(*plVar12 + 0x38))();
    uVar13 = FUN_005494c0();
    if (0 < *piVar15) {
      plVar1 = (long *)(piVar15 + 2);
      sVar10 = 0;
      do {
        lVar11 = (long)sVar10 * 0x10;
        lVar14 = lVar11 + *plVar1;
        lVar11 = *(long *)((long)plVar1 + lVar11 + 0x18 + *plVar1);
        auVar25 = FUN_00549bf0(uVar13,*(undefined1 *)((long)plVar1 + lVar11 + 0xba + lVar14));
        lVar21 = 0;
        lVar23 = *(long *)((long)plVar1 + lVar11 + 0x30 + lVar14);
        if (lVar23 != 0) {
          lVar21 = (long)plVar1 + lVar23 + lVar11 + 0x30 + lVar14;
        }
        if ((((auVar25._0_8_ != 0) && (auVar25._8_8_ != 0)) &&
            (*(char *)(auVar25._8_8_ + 0xb0) == '\x01')) && (lVar21 != 0)) {
          iVar18 = 0;
          if (0 < *(long *)(lVar21 + 8)) {
            psVar16 = (short *)(*(long *)(lVar21 + 0x10) + 0x28 + lVar21);
            iVar18 = 0;
            lVar11 = 0;
            do {
              iVar18 = iVar18 + *(int *)(param_1 + 0x1ae0 + (long)*psVar16 * 4);
              psVar16 = psVar16 + 0x1c;
              lVar11 = lVar11 + 1;
            } while (lVar11 < *(long *)(lVar21 + 8));
          }
          *(int *)(param_1 + 0x1ae0 + (long)sVar10 * 4) = iVar18;
        }
        sVar10 = sVar10 + 1;
      } while ((int)sVar10 < *piVar15);
    }
    local_1a0[0x38] = 0;
    local_1a0[0x39] = 0;
    local_1a0[0x3a] = 0;
    local_1a0[0x3b] = 0;
    local_1a0[0x3c] = 0;
    local_1a0[0x3d] = 0;
    local_1a0[0x3e] = 0;
    local_1a0[0x3f] = 0;
    local_1a0[0x30] = 0;
    local_1a0[0x31] = 0;
    local_1a0[0x32] = 0;
    local_1a0[0x33] = 0;
    local_1a0[0x34] = 0;
    local_1a0[0x35] = 0;
    local_1a0[0x36] = 0;
    local_1a0[0x37] = 0;
    local_1a0[0x28] = 0;
    local_1a0[0x29] = 0;
    local_1a0[0x2a] = 0;
    local_1a0[0x2b] = 0;
    local_1a0[0x2c] = 0;
    local_1a0[0x2d] = 0;
    local_1a0[0x2e] = 0;
    local_1a0[0x2f] = 0;
    local_1a0[0x20] = 0;
    local_1a0[0x21] = 0;
    local_1a0[0x22] = 0;
    local_1a0[0x23] = 0;
    local_1a0[0x24] = 0;
    local_1a0[0x25] = 0;
    local_1a0[0x26] = 0;
    local_1a0[0x27] = 0;
    local_1a0[0x18] = 0;
    local_1a0[0x19] = 0;
    local_1a0[0x1a] = 0;
    local_1a0[0x1b] = 0;
    local_1a0[0x1c] = 0;
    local_1a0[0x1d] = 0;
    local_1a0[0x1e] = 0;
    local_1a0[0x1f] = 0;
    local_1a0[0x10] = 0;
    local_1a0[0x11] = 0;
    local_1a0[0x12] = 0;
    local_1a0[0x13] = 0;
    local_1a0[0x14] = 0;
    local_1a0[0x15] = 0;
    local_1a0[0x16] = 0;
    local_1a0[0x17] = 0;
    local_1a0[8] = 0;
    local_1a0[9] = 0;
    local_1a0[10] = 0;
    local_1a0[0xb] = 0;
    local_1a0[0xc] = 0;
    local_1a0[0xd] = 0;
    local_1a0[0xe] = 0;
    local_1a0[0xf] = 0;
    local_1a0[0] = 0;
    local_1a0[1] = 0;
    local_1a0[2] = 0;
    local_1a0[3] = 0;
    local_1a0[4] = 0;
    local_1a0[5] = 0;
    local_1a0[6] = 0;
    local_1a0[7] = 0;
    FUN_00267470(local_520,param_2);
    FUN_00267480(local_520);
    cVar6 = FUN_00267580(local_520);
    if (cVar6 != '\0') {
      do {
        cVar6 = FUN_00267630(local_520);
        lVar11 = FUN_00267640(local_520);
        if (0 < *(long *)(lVar11 + 8)) {
          lVar23 = 0;
          do {
            lVar21 = (long)cVar6 * 0x4c + param_1;
            cVar8 = *(char *)(lVar23 + 0x5e8 + lVar21);
            lVar14 = *(long *)(lVar11 + 0x10);
            iVar18 = FUN_00264360(param_2);
            puVar2 = (undefined1 *)(lVar23 + 0x5e8 + lVar21);
            uVar9 = (undefined1)iVar18;
            if ((cVar8 < iVar18) && (*(char *)(param_1 + 0x42e8) != '\0')) {
              if (3 < iVar18) {
                uVar7 = FUN_00267630(local_520);
                *(undefined1 *)(param_1 + 0x42e0) = uVar7;
                *(byte *)(param_1 + 0x42e1) = (byte)lVar23;
                *puVar2 = uVar9;
                goto LAB_005902ca;
              }
              if (2 < iVar18) {
                puVar3 = (uint *)(lVar21 + 0x5e0 + (long)((int)lVar23 >> 5) * 4);
                *puVar3 = *puVar3 | 1 << ((byte)lVar23 & 0x1f);
                goto LAB_005902c0;
              }
              *puVar2 = uVar9;
            }
            else {
LAB_005902c0:
              *puVar2 = uVar9;
              if (2 < iVar18) {
LAB_005902ca:
                FUN_00263c10(local_538,param_2,lVar11 + 0x10 + lVar23 * 0x28 + lVar14 + 0x10);
                FUN_00263c20(local_538);
                while (cVar8 = FUN_00263d30(local_538), cVar8 != '\0') {
                  sVar10 = FUN_00263d70(local_538);
                  local_1a0[(int)sVar10 >> 5] =
                       local_1a0[(int)sVar10 >> 5] | 1 << ((byte)sVar10 & 0x1f);
                  FUN_00263cb0(local_538);
                }
              }
            }
            lVar23 = lVar23 + 1;
          } while (lVar23 < *(long *)(lVar11 + 8));
        }
        thunk_FUN_00267490(local_520);
        cVar6 = FUN_00267580(local_520);
      } while (cVar6 != '\0');
    }
    FUN_00267e00(param_2,local_1a0,local_4a0);
    thunk_FUN_012aa7c6(param_1 + 0x18e0,local_3a0,0x100);
    thunk_FUN_012aa7c6(param_1 + 0x19e0,local_2a0,0x100);
    lVar11 = (**(code **)(*plVar12 + 0xc0))();
    local_4f8 = 0;
    FUN_00268110(param_2,lVar11,lVar11 + 0x10,local_4a0,0,&local_4f8);
    if (0 < local_4f8) {
      lVar11 = 0;
      do {
        *(undefined1 *)(param_1 + 0x3ae0 + (long)*(short *)(auStack_4f2 + lVar11 * 4 + -2)) =
             auStack_4f2[lVar11 * 4];
        lVar11 = lVar11 + 1;
      } while ((int)lVar11 < local_4f8);
    }
    FUN_00267470(local_558,param_2);
    local_540 = param_1 + 0x5e0;
    FUN_00267480(local_558);
    cVar6 = FUN_00267580(local_558);
    if (cVar6 != '\0') {
      do {
        cVar6 = FUN_00267630(local_558);
        lVar23 = (long)cVar6 * 0x4c;
        *(undefined4 *)(param_1 + 0x628 + lVar23) = 0;
        FUN_00267630(local_558);
        uVar13 = FUN_005494c0();
        uVar9 = FUN_00267630(local_558);
        auVar25 = FUN_00549a20(uVar13,uVar9);
        lVar11 = local_540;
        uVar13 = local_558[0];
        cVar6 = FUN_00267630(local_558);
        FUN_00263db0(&local_588,uVar13,auVar25._0_8_,lVar11 + 8 + (long)cVar6 * 0x4c,cVar6);
        local_560 = lVar11;
        local_568 = auVar25._8_8_;
        FUN_00263dd0(&local_588);
        while (cVar6 = FUN_00263eb0(&local_588), lVar11 = local_560, cVar6 != '\0') {
          FUN_00263c10(local_5a8,local_588,
                       local_580 + *(long *)(local_580 + 0x10) + 0x20 + (long)local_56f * 0x28);
          local_590 = lVar11;
          FUN_00263c20(local_5a8);
          while (cVar6 = FUN_00263d30(local_5a8), cVar6 != '\0') {
            lVar11 = FUN_00263d90(local_5a8);
            bVar4 = *(byte *)(local_590 + 0x3500 + (long)*(short *)(lVar11 + 4));
            if ((char)bVar4 != -1) {
              puVar3 = (uint *)(param_1 + lVar23 + 0x628 + (long)((int)(char)bVar4 >> 5) * 4);
              *puVar3 = *puVar3 | 1 << (bVar4 & 0x1f);
            }
            FUN_00263cb0(local_5a8);
          }
          iVar18 = FUN_005451a0(param_2,(long)local_56f * 0x50 +
                                        local_568 + 0x28 + *(long *)(local_568 + 0x18));
          if (iVar18 != -1) {
            puVar3 = (uint *)(param_1 + lVar23 + 0x628 + (long)(iVar18 >> 5) * 4);
            *puVar3 = *puVar3 | 1 << ((byte)iVar18 & 0x1f);
          }
          FUN_00263e40(&local_588);
        }
        thunk_FUN_00267490(local_558);
        cVar6 = FUN_00267580(local_558);
      } while (cVar6 != '\0');
    }
    *(undefined1 *)(param_1 + 0x42e8) = 1;
    *(byte *)(param_1 + 0x4580) = *(byte *)(param_1 + 0x4580) & 0xfe;
  }
  if (*DAT_01a1f100 != local_60) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

