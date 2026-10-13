
/* WARNING: Removing unreachable block (ram,0x005947f8) */
/* WARNING: Removing unreachable block (ram,0x00594498) */
/* WARNING: Removing unreachable block (ram,0x00594798) */
/* WARNING: Removing unreachable block (ram,0x00594938) */
/* WARNING: Removing unreachable block (ram,0x00594558) */
/* WARNING: Removing unreachable block (ram,0x00594588) */
/* WARNING: Removing unreachable block (ram,0x00594c58) */
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_00594460(void)

{
  int iVar1;
  ulong uVar2;
  long *plVar3;
  byte bVar4;
  char cVar5;
  byte bVar6;
  long lVar7;
  long lVar8;
  uint uVar9;
  long lVar10;
  long lVar11;
  uint uVar12;
  undefined8 uVar13;
  long lVar14;
  ulong uVar15;
  long *in_FS_OFFSET;
  float fVar16;
  undefined1 auVar17 [16];
  undefined1 local_40 [8];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  LOCK();
  DAT_026bcd30 = 1;
  UNLOCK();
  *(undefined1 *)(*in_FS_OFFSET + _DAT_01a1f418) = 1;
  do {
    FUN_000672a0();
    FUN_000c59d0();
    bVar4 = FUN_00752710();
    uVar12 = (uint)bVar4;
    if ((DAT_026bcd3c != 0) || (cVar5 = FUN_00752730(), cVar5 != '\0')) {
      uVar12 = bVar4 | 2;
    }
    cVar5 = FUN_000014d0();
    uVar9 = uVar12 & 0xfffffffb;
    if (cVar5 != '\0') {
      uVar9 = uVar12 | 4;
    }
    cVar5 = FUN_000c72b0();
    uVar12 = uVar9 & 0xffffffef;
    if (cVar5 != '\0') {
      uVar12 = uVar9 | 0x10;
    }
    *(uint *)(DAT_026bcd18 + 0xf) = uVar12;
    plVar3 = DAT_026bcd18;
    if ((uVar12 & 0x1f) == 0) {
      LOCK();
      DAT_026bcd34 = 0;
      UNLOCK();
      if (DAT_026bcd38 != 0) {
        LOCK();
        DAT_026bcd38 = 0;
        UNLOCK();
        FUN_00592900();
        *(undefined1 *)((long)plVar3 + 0x7c) = 1;
      }
      plVar3 = DAT_026bcd18;
      lVar7 = thunk_FUN_012aac96();
      lVar10 = (long)((float)(lVar7 - plVar3[1]) / *(float *)(plVar3 + 5));
      lVar14 = *plVar3 + lVar10;
      if (1000000 < lVar10) {
        plVar3[1] = lVar7;
        *plVar3 = lVar14;
      }
      plVar3 = DAT_026bcd18;
      uVar9 = (int)*DAT_026bcd10 >> 0xd;
      lVar7 = *DAT_01a238a0;
      lVar8 = (ulong)((uVar9 >> 0x12 | 0x3ff) & uVar9) * 0x40;
      lVar10 = *(long *)(lVar7 + 0x10 + lVar8);
      uVar15 = (ulong)((*DAT_026bcd10 & 0x1fff) * *(int *)(lVar7 + 0x30 + lVar8));
      uVar2 = *(ulong *)(uVar15 + 8 + lVar10);
      iVar1 = *(int *)(lVar7 + 0x34 + lVar8);
      cVar5 = FUN_007e9a10();
      if (cVar5 == '\0') {
        lVar7 = DAT_026bcd18[2];
      }
      else {
        lVar7 = DAT_026bcd18[2];
        if (*(int *)(((lVar10 + uVar15) - (uVar2 & (long)iVar1)) + 0x40) == 0) {
          if (*DAT_026bcd08 == 2) {
            lVar8 = (long)((float)(DAT_026bcd28 - DAT_026bcd18[1]) / *(float *)(DAT_026bcd18 + 5)) +
                    *DAT_026bcd18;
            lVar10 = lVar7 + *(long *)(DAT_026bcd08 + 0xc);
            if (lVar7 + *(long *)(DAT_026bcd08 + 0xc) < lVar14) {
              lVar10 = lVar14;
            }
            lVar10 = lVar10 - lVar8;
            if (lVar10 < 0) {
              lVar10 = 0;
            }
            lVar7 = *(long *)(DAT_026bcd08 + 6);
            lVar11 = lVar10 % *(long *)(DAT_026bcd08 + 10);
            if (lVar11 < lVar7) {
              lVar7 = (lVar8 - lVar11) + lVar7 + lVar10;
            }
            else if (lVar11 < *(long *)(DAT_026bcd08 + 8)) {
              lVar7 = lVar8 + lVar10;
            }
            else {
              lVar7 = ((*(long *)(DAT_026bcd08 + 10) + lVar8) - lVar11) + lVar7 + lVar10;
            }
          }
          else {
            lVar7 = lVar7 + *(long *)(DAT_026bcd08 + 2);
          }
        }
      }
      cVar5 = FUN_0023cec0(DAT_026ec3a0);
      bVar4 = 0;
      if (cVar5 != '\0') {
        bVar4 = FUN_0023cec0(DAT_026ec43c);
      }
      bVar6 = 1;
      if (*(short *)((long)plVar3 + 0x34) != -1) {
        bVar6 = FUN_000fba50(plVar3[6]);
      }
      bVar4 = bVar4 & bVar6;
      if (lVar7 - lVar14 < 0xe) {
        fVar16 = DAT_0163ea6c;
        if (bVar4 != 0) {
          plVar3[2] = lVar14;
          FUN_00593970(lVar14);
          FUN_0023ab00();
          FUN_00000380();
          lVar14 = 0;
          uVar13 = 1;
          bVar4 = 1;
          fVar16 = DAT_0163ea70;
          goto LAB_00594b80;
        }
      }
      else {
        fVar16 = DAT_0163ea64;
        if (bVar4 != 0) {
          auVar17._4_12_ = SUB6012((undefined1  [60])0x0,0);
          auVar17._0_4_ = (float)((lVar7 - lVar14) + -0xd) / DAT_0163ea68;
          auVar17 = vmaxss_avx(auVar17,ZEXT416((uint)DAT_0163ea7c));
          fVar16 = auVar17._0_4_;
        }
      }
      bVar4 = bVar4 ^ 1;
LAB_00594b15:
      uVar13 = 0;
    }
    else {
      if (*(char *)((long)DAT_026bcd18 + 0x7c) != '\0') {
        *(undefined1 *)((long)DAT_026bcd18 + 0x7c) = 0;
        if (((DAT_026bcce0 != '\0') && (*(short *)((long)plVar3 + 0x4c) != -1)) &&
           (*(short *)((long)plVar3 + 0x54) != -1)) {
          if (DAT_026bcce1 != '\0') {
            FUN_000fb630(plVar3[9]);
            *(undefined4 *)(plVar3 + 9) = 0;
            *(undefined4 *)((long)plVar3 + 0x4c) = 0xffff;
          }
          FUN_000fb630(plVar3[10]);
          *(undefined4 *)(plVar3 + 10) = 0;
          *(undefined4 *)((long)plVar3 + 0x54) = 0xffff;
        }
        FUN_005928e0();
      }
      if (((DAT_026bcd34 == 0) && (cVar5 = FUN_0023ce80(DAT_026c6fd0), cVar5 != '\0')) &&
         ((cVar5 = FUN_0023ce80(DAT_026ec3a0), cVar5 != '\0' &&
          (cVar5 = FUN_0023ce80(DAT_026ec43c), cVar5 != '\0')))) {
        LOCK();
        DAT_026bcd34 = 1;
        UNLOCK();
      }
      if (((DAT_026bcd38 == 0) && (cVar5 = FUN_00592920(), cVar5 != '\0')) && (DAT_026bcd34 != 0)) {
        bVar4 = 1;
        if (*(short *)((long)plVar3 + 0x44) != -1) {
          bVar4 = FUN_000fba50(plVar3[8]);
        }
        LOCK();
        DAT_026bcd38 = (uint)bVar4;
        UNLOCK();
      }
      plVar3 = DAT_026bcd18;
      if (DAT_026bcd38 == 0) {
        if (DAT_026bcd34 == 0) {
          bVar4 = 1;
          lVar14 = 0;
          uVar13 = 0;
          fVar16 = DAT_0163ea60;
          if ((*DAT_026bcd08 != 0) && (DAT_026bcd40 == 0)) {
            if (*(short *)((long)DAT_026bcd18 + 0x3c) != -1) {
              uVar2 = DAT_026bcd18[8];
              lVar7 = FUN_000fb400(0,DAT_026bcdd0,DAT_025d12ad,DAT_025d11c0,(undefined4)DAT_025d11c8
                                   ,DAT_025d11c0,DAT_025d11c0,
                                   CONCAT44(DAT_025d11c8._4_4_,(undefined4)DAT_025d11c8),
                                   DAT_025d11c0,
                                   CONCAT44(DAT_025d11c8._4_4_,(undefined4)DAT_025d11c8),
                                   DAT_025d11c0,
                                   CONCAT44(DAT_025d11c8._4_4_,(undefined4)DAT_025d11c8));
              plVar3[8] = lVar7;
              FUN_000fb6e0(lVar7,plVar3[6]);
              FUN_000fb6e0(plVar3[8],plVar3[7]);
              if ((uVar2 & 0xffff00000000) != 0xffff00000000) {
                FUN_000fb6e0(plVar3[8],uVar2);
              }
              LOCK();
              DAT_026bcd40 = 1;
              UNLOCK();
              FUN_000fb5c0(plVar3[8]);
              fVar16 = DAT_0163ea60;
            }
            goto LAB_00594b15;
          }
        }
        else {
          bVar4 = 1;
          lVar14 = 0;
          uVar13 = 0;
          fVar16 = DAT_0163ea5c;
          if ((DAT_018dcaad != '\0') &&
             (lVar7 = FUN_00ae3640(), fVar16 = DAT_0163ea5c, *(char *)(lVar7 + 1) == '\0')) {
            cVar5 = FUN_00592670();
            if (cVar5 == '\0') {
              FUN_00592650(local_40);
              FUN_00ae8a40();
              FUN_001d2800();
              FUN_00ae8710();
              thunk_FUN_00b2a170();
              FUN_00ae3a40();
              FUN_00ae8060();
              FUN_00ae8370();
              FUN_00ae81d0();
              FUN_001d2800();
              FUN_00ae8a50();
              FUN_00592690(local_40);
              fVar16 = DAT_0163ea5c;
            }
            else {
              FUN_00ae8a40();
              FUN_001d2800();
              FUN_00ae8710();
              thunk_FUN_00b2a170();
              FUN_00ae3a40();
              FUN_00ae8060();
              FUN_00ae8370();
              FUN_00ae81d0();
              FUN_001d2800();
              FUN_00ae8a50();
              fVar16 = DAT_0163ea5c;
            }
          }
        }
      }
      else {
        if ((uVar12 & 3) != 0) {
          FUN_005938e0((uVar12 & 2) >> 1);
        }
        if ((uVar12 & 4) != 0) {
          FUN_000f8210();
        }
        if ((uVar12 & 0x10) != 0) {
          FUN_000c6fc0();
        }
        *(undefined4 *)(DAT_026bcd18 + 0xf) = 0;
        lVar14 = 0;
        uVar13 = 0;
        fVar16 = 0.0;
        bVar4 = 0;
      }
    }
LAB_00594b80:
    FUN_000f8210(uVar13);
    if (((uVar12 & 2) != 0) && (DAT_026bcd38 != 0)) {
      LOCK();
      DAT_026bcd30 = 0;
      UNLOCK();
      *(undefined1 *)(*in_FS_OFFSET + _DAT_01a1f418) = 0;
      if (*DAT_01a1f100 == local_38) {
        return;
      }
      thunk_FUN_012aa7f6();
      return;
    }
    if ((DAT_0163ea74 < fVar16 | bVar4) == 1) {
      iVar1 = (int)(fVar16 + DAT_0163ea78);
      if ((int)(fVar16 + DAT_0163ea78) < 1) {
        iVar1 = 1;
      }
      FUN_000f4f80(DAT_026bcd44,iVar1);
    }
    else if (DAT_0163ea7c < fVar16) {
      fVar16 = fVar16 * DAT_0163ea68;
      uVar12 = 0;
      do {
        for (; plVar3 = DAT_026bcd18, uVar12 < 0x32; uVar12 = uVar12 + 1) {
        }
        lVar7 = thunk_FUN_012aac96();
        lVar8 = (long)((float)(lVar7 - plVar3[1]) / *(float *)(plVar3 + 5));
        lVar10 = *plVar3 + lVar8;
        if (1000000 < lVar8) {
          plVar3[1] = lVar7;
          *plVar3 = lVar10;
        }
        uVar12 = 0;
      } while (lVar10 - lVar14 < (long)fVar16);
    }
  } while( true );
}

