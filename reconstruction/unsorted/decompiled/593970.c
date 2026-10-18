
/* WARNING: Removing unreachable block (ram,0x00593d4a) */

void FUN_00593970(long param_1)

{
  long lVar1;
  long lVar2;
  long lVar3;
  int *piVar4;
  undefined4 *puVar5;
  long lVar6;
  uint uVar7;
  ulong uVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  undefined8 uVar12;
  long lVar13;
  ulong uVar14;
  
  lVar1 = *DAT_01a1f100;
  FUN_007e9a10();
  lVar6 = DAT_026bcd18;
  piVar4 = DAT_026bcd08;
  if (*(long *)(DAT_026bcd08 + 4) < param_1 - *(long *)(DAT_026bcd18 + 0x18)) {
    FUN_000ccfa0();
    *(long *)(lVar6 + 0x20) = *(long *)(lVar6 + 0x20) + 1;
    *(long *)(lVar6 + 0x18) = param_1;
  }
  puVar5 = DAT_026bcd10;
  uVar7 = DAT_026bcd10[3];
  DAT_026bcd10[3] = uVar7 ^ 1;
  uVar14 = (long)(int)uVar7 ^ 1;
  if (puVar5[uVar14 + 1] != -1) {
    FUN_0006ecb0(&DAT_026bcd50);
  }
  uVar7 = FUN_0006e750(&DAT_026bcd50);
  puVar5[uVar14 + 1] = uVar7;
  lVar2 = DAT_026bcd58;
  uVar8 = (ulong)((uVar7 & 0x1fff) * DAT_026bcd60);
  *(undefined8 *)(DAT_026bcd58 + 0x40 + uVar8) = 0;
  *(undefined8 *)(lVar2 + 0x38 + uVar8) = 0;
  *(undefined8 *)(lVar2 + 0x30 + uVar8) = 0;
  *(undefined8 *)(lVar2 + 0x28 + uVar8) = 0;
  *(undefined8 *)(lVar2 + 0x20 + uVar8) = 0;
  *(undefined8 *)(lVar2 + 0x18 + uVar8) = 0;
  *(undefined8 *)(lVar2 + 0x10 + uVar8) = 0;
  *(undefined8 *)(lVar2 + 8 + uVar8) = 0;
  *(undefined8 *)(lVar2 + uVar8) = 0;
  *(long *)(lVar2 + uVar8) = param_1;
  *(undefined8 *)(lVar2 + 0x38 + uVar8) = *(undefined8 *)(piVar4 + 0x10);
  FUN_00591d40(*puVar5,puVar5[uVar14 + 1]);
  *(undefined8 *)(lVar6 + 0x20) = 0;
  uVar9 = thunk_FUN_0023cb40(DAT_026c6fd0);
  uVar10 = thunk_FUN_0023cb40(DAT_026ec3a0);
  uVar11 = thunk_FUN_0023cb40(DAT_026ec43c);
  FUN_0023d160(DAT_026ec3a0,uVar10,0,DAT_026c6fd0,uVar9,1);
  FUN_0023d160(DAT_026ec3a0,uVar10,1,DAT_026c6fd0,uVar9,10);
  FUN_0023d160(DAT_026ec3a0,uVar10,2,DAT_026c6fd0,uVar9,0xb);
  FUN_0023d160(DAT_026ec3a0,uVar10,4,DAT_026c6fd0,uVar9,0xc);
  FUN_0023d160(DAT_026c6fd0,uVar9,0xd,DAT_026ec3a0,uVar10,5);
  FUN_0023d160(DAT_026ec43c,uVar11,0,DAT_026ec3a0,uVar10,7);
  if (DAT_018dcab4 != '\0') {
    FUN_0023d160(DAT_026c6fd0,uVar9,0xc,DAT_026ec3a0,uVar10,3);
  }
  if ((DAT_018dcaac != '\0') && (*(short *)(lVar6 + 0x54) != -1)) {
    uVar12 = FUN_0023cf00(DAT_026ec3a0,uVar10,1);
    FUN_000fb6e0(uVar12,*(undefined8 *)(lVar6 + 0x50));
  }
  if (((DAT_026bcce0 != '\0') && (*(short *)(lVar6 + 0x4c) != -1)) &&
     (*(short *)(lVar6 + 0x54) != -1)) {
    uVar12 = FUN_0023cf00(DAT_026c6fd0,uVar9,8);
    if (DAT_026bcce1 != '\0') {
      FUN_000fb670(*(undefined8 *)(lVar6 + 0x48),uVar12);
      FUN_000fb630(*(undefined8 *)(lVar6 + 0x48));
    }
    FUN_000fb670(*(undefined8 *)(lVar6 + 0x50),uVar12);
    FUN_000fb630(*(undefined8 *)(lVar6 + 0x50));
  }
  uVar12 = FUN_0023cf00(DAT_026ec43c,uVar11,0);
  *(undefined8 *)(lVar6 + 0x48) = uVar12;
  if ((DAT_026bcce0 != '\0') && (DAT_026bcce1 != '\0')) {
    FUN_000fb610(uVar12);
  }
  uVar12 = FUN_0023cf00(DAT_026ec43c,uVar11,1);
  *(undefined8 *)(lVar6 + 0x50) = uVar12;
  if (DAT_026bcce0 != '\0') {
    FUN_000fb610(uVar12);
  }
  if (*(short *)(lVar6 + 0x3c) != -1) {
    uVar12 = FUN_0023cf00(DAT_026ec3a0,uVar10,6);
    FUN_000fb6e0(uVar12,*(undefined8 *)(lVar6 + 0x38));
  }
  if (*(short *)(lVar6 + 0x5c) != -1) {
    uVar12 = FUN_0023cf00(DAT_026c6fd0,uVar9,0xb);
    FUN_000fb6e0(uVar12,*(undefined8 *)(lVar6 + 0x58));
  }
  uVar14 = *(ulong *)(lVar6 + 0x38);
  uVar12 = FUN_0023cf00(DAT_026ec43c,uVar11,6);
  *(undefined8 *)(lVar6 + 0x38) = uVar12;
  uVar12 = FUN_0023cf00(DAT_026ec3a0,uVar10,7);
  *(undefined8 *)(lVar6 + 0x58) = uVar12;
  *(undefined8 *)(lVar6 + 0x68) = uVar10;
  *(undefined8 *)(lVar6 + 0x70) = uVar11;
  LOCK();
  UNLOCK();
  DAT_026bcd20 = uVar10;
  *(undefined8 *)(lVar6 + 0x60) = uVar9;
  FUN_0023cf00(DAT_026c6fd0,uVar9,0);
  lVar13 = (ulong)(((uint)((int)DAT_026c6fd0 >> 0xd) >> 0x12 | 0x3ff) & (int)DAT_026c6fd0 >> 0xd) *
           0x40;
  lVar2 = *DAT_01a238a0;
  lVar3 = *(long *)(lVar2 + 0x10 + lVar13);
  uVar8 = (ulong)((DAT_026c6fd0 & 0x1fff) * *(int *)(lVar2 + 0x30 + lVar13));
  uVar9 = FUN_0023cf00(DAT_026c6fd0,*(undefined8 *)(lVar6 + 0x60),
                       *(int *)(((lVar3 + uVar8) -
                                ((long)*(int *)(lVar2 + 0x34 + lVar13) &
                                *(ulong *)(lVar3 + 8 + uVar8))) + 0x10) + -1);
  *(undefined8 *)(lVar6 + 0x30) = uVar9;
  thunk_FUN_0023cdc0(DAT_026c6fd0,*(undefined8 *)(lVar6 + 0x60));
  thunk_FUN_0023cdc0(DAT_026ec3a0,*(undefined8 *)(lVar6 + 0x68));
  thunk_FUN_0023cdc0(DAT_026ec43c,*(undefined8 *)(lVar6 + 0x70));
  if (*piVar4 != 0) {
    uVar8 = *(ulong *)(lVar6 + 0x40);
    uVar9 = FUN_000fb400(0,DAT_026bcdd0,DAT_025d12ad,DAT_025d11c0,(undefined4)DAT_025d11c8);
    *(undefined8 *)(lVar6 + 0x40) = uVar9;
    FUN_000fb6e0(uVar9,*(undefined8 *)(lVar6 + 0x30));
    if ((uVar14 & 0xffff00000000) != 0xffff00000000) {
      FUN_000fb6e0(*(undefined8 *)(lVar6 + 0x40));
    }
    if ((uVar8 & 0xffff00000000) != 0xffff00000000) {
      FUN_000fb6e0(*(undefined8 *)(lVar6 + 0x40),uVar8);
    }
    LOCK();
    DAT_026bcd40 = DAT_026bcd40 + 1;
    UNLOCK();
    FUN_000fb5c0(*(undefined8 *)(lVar6 + 0x40));
  }
  if (*DAT_01a1f100 != lVar1) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

