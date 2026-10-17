
void FUN_0091e000(float param_1,undefined4 param_2,int param_3,uint param_4,long param_5,
                 long param_6)

{
  uint *puVar1;
  byte *pbVar2;
  char *pcVar3;
  long lVar4;
  char cVar5;
  char cVar6;
  char cVar7;
  char cVar8;
  char cVar9;
  char cVar10;
  char cVar11;
  byte bVar12;
  short sVar13;
  uint uVar14;
  int iVar15;
  uint uVar16;
  undefined4 uVar17;
  ulong uVar18;
  undefined8 uVar19;
  long lVar20;
  undefined1 *puVar21;
  char *pcVar22;
  undefined1 uVar23;
  long lVar24;
  uint *puVar25;
  short *psVar26;
  bool bVar27;
  bool bVar28;
  float fVar29;
  undefined4 uVar30;
  undefined1 auVar31 [16];
  char local_55;
  
  lVar4 = DAT_0273eb28;
  if (3 < param_4) {
    return;
  }
  lVar24 = (long)param_3 * 0x1a0;
  puVar1 = (uint *)(DAT_0273eb28 + 0x20 + lVar24);
  bVar28 = false;
  bVar27 = false;
  if ((*puVar1 != 0xffffffff) &&
     (uVar18 = (ulong)((*puVar1 & 0x1fff) * DAT_02689800),
     uVar18 = (ulong)((*(uint *)(((uVar18 + DAT_026897f8) -
                                 (*(ulong *)(DAT_026897f8 + 8 + uVar18) & (long)DAT_02689818)) +
                                0x68) & 0x1fff) * DAT_02689800), bVar27 = false,
     *(int *)(((DAT_026897f8 + uVar18) -
              ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar18))) + 0x7a0) != -1)) {
    uVar14 = FUN_006ed8f0();
    bVar27 = *(int *)((ulong)((uVar14 & 0x1fff) * DAT_02692230) + 0x44 + DAT_02692228) != -1;
  }
  FUN_0091b500(param_1,param_2,param_3,param_4,param_5,puVar1,param_6);
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1a4) * 0x14) = 0;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1a4);
  if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
     ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
      (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) {
    bVar28 = *(char *)(param_5 + 2 + uVar18 * 0x14) != '\0';
  }
  auVar31._0_12_ = ZEXT812(0);
  auVar31._12_4_ = 0;
  auVar31 = vmaxss_avx(ZEXT416((uint)(*(float *)(lVar4 + 0x158 + lVar24) - param_1)),auVar31);
  fVar29 = auVar31._0_4_;
  *(float *)(lVar4 + 0x158 + lVar24) = fVar29;
  puVar25 = (uint *)(lVar4 + 0x15c + lVar24);
  switch(*(undefined4 *)(lVar4 + 0x15c + lVar24)) {
  case 0:
    if (bVar28 != false) {
      *puVar25 = 2;
    }
    break;
  case 1:
    if (bVar28 == false) {
      *puVar25 = 0;
    }
    break;
  case 2:
    if (bVar28 == false) {
      *puVar25 = 3;
    }
    break;
  case 3:
    if (bVar28 != false) {
      *puVar25 = 4;
    }
  }
  if ((fVar29 == 0.0) && (!NAN(fVar29))) {
    *puVar25 = (uint)bVar28;
  }
  uVar19 = FUN_00945950(param_4);
  uVar19 = FUN_009461c0(uVar19);
  cVar5 = FUN_00947ed0(uVar19);
  cVar6 = FUN_008e3b10(param_3);
  uVar19 = FUN_00958d30();
  cVar7 = FUN_00959fc0(uVar19,param_4);
  local_55 = '\0';
  cVar8 = FUN_009299b0();
  cVar9 = FUN_003f6ff0();
  cVar11 = '\0';
  if (*puVar1 != 0xffffffff) {
    cVar10 = FUN_00bcf9e0();
    cVar11 = '\0';
    local_55 = '\0';
    if (cVar10 != '\0') {
      local_55 = FUN_00bd1030(*puVar1);
    }
    if ((*puVar1 != 0xffffffff) && (iVar15 = FUN_00bd3540(), iVar15 != -1)) {
      cVar11 = FUN_00bc9d80(iVar15);
    }
  }
  if (((cVar6 == '\0' && cVar7 == '\0') && cVar8 == '\0') && cVar9 == '\0') {
    if (cVar11 == '\0') {
      *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1c4) * 0x14) = 8;
      uVar18 = (ulong)*(uint *)(param_5 + 0x1c4);
      bVar28 = false;
      if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
         ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
          (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) {
        bVar28 = *(char *)(param_5 + 2 + uVar18 * 0x14) == '\x01';
      }
      if (cVar5 == '\x01' && local_55 == '\0') {
        if (bVar28) {
          pbVar2 = (byte *)(lVar4 + 0x174 + lVar24);
          bVar12 = *(byte *)(lVar4 + 0x174 + lVar24);
          if (bVar12 == 0) {
            fVar29 = (float)FUN_000a9a10(param_6);
            if (DAT_0166b6fc <= fVar29) goto LAB_0091ed5d;
            bVar12 = *pbVar2;
          }
          *pbVar2 = bVar12 ^ 1;
        }
LAB_0091ed5d:
        *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1c4) * 0x14) = 8;
        uVar18 = (ulong)*(uint *)(param_5 + 0x1c4);
        if ((((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) != 0) ||
            (((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 != 0x25 &&
              (iVar15 != *(int *)(param_5 + 0xc + uVar18 * 0x14))) ||
             (*(char *)(param_5 + 2 + uVar18 * 0x14) == '\0')))) &&
           (0xe < *(short *)(lVar4 + 0x176 + lVar24))) {
          *(undefined1 *)(lVar4 + 0x174 + lVar24) = 0;
          uVar18 = (ulong)*(uint *)(param_5 + 0x1c4);
        }
        *(undefined4 *)(param_5 + 0xc + uVar18 * 0x14) = 8;
        uVar18 = (ulong)*(uint *)(param_5 + 0x1c4);
        if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
           ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
            (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) {
          psVar26 = (short *)(lVar4 + 0x176 + lVar24);
          sVar13 = 0;
          if (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0') {
            sVar13 = *psVar26 + 1;
          }
        }
        else {
          psVar26 = (short *)(lVar4 + 0x176 + lVar24);
          sVar13 = 0;
        }
        *psVar26 = sVar13;
        uVar14 = FUN_009230f0(param_3);
        if ((uVar14 != 0xffffffff) &&
           ((*(byte *)(*(long *)(DAT_0273ea80 + 8) + 0x611 + (ulong)(uVar14 & 0xffff) * 0x2af0) & 2)
            != 0)) {
          *(undefined1 *)(lVar4 + 0x174 + lVar24) = 0;
          *psVar26 = 0;
        }
        goto LAB_0091e333;
      }
      if ((bVar28) &&
         ((local_55 != '\0' || (fVar29 = (float)FUN_000a9a10(), fVar29 < DAT_0166b6fc)))) {
        *(undefined1 *)(lVar4 + 0x174 + lVar24) = 1;
      }
      *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1c4) * 0x14) = 8;
      uVar18 = (ulong)*(uint *)(param_5 + 0x1c4);
      if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
         (((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
           (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))) &&
          (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')))) goto LAB_0091e333;
    }
    *(undefined1 *)(lVar4 + 0x174 + lVar24) = 0;
  }
LAB_0091e333:
  pcVar22 = (char *)(lVar4 + 0x174 + lVar24);
  if (*(char *)(lVar4 + 0x174 + lVar24) == '\0') {
    uVar14 = *(uint *)(param_6 + 0x20) & 0xfffffffe;
  }
  else {
    uVar14 = *(uint *)(param_6 + 0x20) | 1;
  }
  *(uint *)(param_6 + 0x20) = uVar14;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1c8) * 0x14) = 9;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1c8);
  cVar6 = '\0';
  if ((((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
      ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
       (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) &&
     (cVar6 = *(char *)(param_5 + 2 + uVar18 * 0x14), cVar6 == '\x01')) {
    if (*(short *)(lVar4 + 0x6e + lVar24) == -1) {
      if (*puVar1 != 0xffffffff) {
        FUN_00bd3540();
        if (*puVar1 != 0xffffffff) {
          uVar18 = (ulong)((*puVar1 & 0x1fff) * DAT_02689800);
          uVar18 = (ulong)((*(uint *)(((uVar18 + DAT_026897f8) -
                                      (*(ulong *)(DAT_026897f8 + 8 + uVar18) & (long)DAT_02689818))
                                     + 0x68) & 0x1fff) * DAT_02689800);
          uVar14 = *(uint *)(((DAT_026897f8 + uVar18) -
                             ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar18))) + 0x7a0);
          uVar16 = FUN_006ed8f0();
          if (((*(int *)((ulong)((uVar16 & 0x1fff) * DAT_02692230) + 0x44 + DAT_02692228) != -1) &&
              (uVar14 != 0xffffffff)) &&
             (uVar18 = (ulong)((uVar14 & 0x1fff) * DAT_02689800),
             lVar20 = FUN_00102980((DAT_026897f8 + uVar18) -
                                   ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar18))),
             (*(byte *)(lVar20 + 0xb8) & 4) != 0)) {
            uVar14 = FUN_006ed8f0(*puVar1);
            uVar17 = FUN_006ed9f0(*(undefined4 *)
                                   ((ulong)((uVar14 & 0x1fff) * DAT_02692230) + 0x44 + DAT_02692228)
                                 );
            FUN_00bd3540(uVar17);
          }
        }
      }
      if ((((*(byte *)(param_5 + 4) & 1) == 0) &&
          (((*(int *)(param_5 + 0x10) == 0x25 ||
            (*(int *)(param_5 + 0x10) == *(int *)(param_5 + 0xc))) &&
           (cVar6 = '\x01', DAT_0166b700 < *(float *)(param_5 + 8))))) ||
         ((((*(byte *)(param_5 + 0x18) & 1) == 0 &&
           ((*(int *)(param_5 + 0x24) == 0x25 ||
            (*(int *)(param_5 + 0x24) == *(int *)(param_5 + 0x20))))) &&
          (cVar6 = '\x01', DAT_0166b700 < *(float *)(param_5 + 0x1c))))) goto LAB_0091e50d;
    }
    uVar14 = *(uint *)(param_6 + 0x24) | 4;
    *(uint *)(param_6 + 0x24) = uVar14;
    cVar6 = '\x01';
  }
  else {
LAB_0091e50d:
    uVar14 = *(uint *)(param_6 + 0x24) & 0xfffffffb;
    *(uint *)(param_6 + 0x24) = uVar14;
  }
  puVar25 = (uint *)(param_6 + 0x24);
  uVar16 = uVar14 | 8;
  if (cVar6 == '\0') {
    uVar16 = uVar14 & 0xfffffff7;
  }
  *puVar25 = uVar16;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1c0) * 0x14) = 7;
  uVar30 = 0;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1c0);
  uVar17 = 0;
  if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
     ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
      (uVar17 = 0, iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) {
    uVar17 = *(undefined4 *)(param_5 + 8 + uVar18 * 0x14);
  }
  *(undefined4 *)(param_6 + 8) = uVar17;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1cc) * 0x14) = 10;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1cc);
  if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
     ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
      (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) {
    uVar30 = *(undefined4 *)(param_5 + 8 + uVar18 * 0x14);
  }
  *(undefined4 *)(param_6 + 0xc) = uVar30;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1cc) * 0x14) = 10;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1cc);
  iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14);
  if ((iVar15 != 0x25) && (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))) {
    pbVar2 = (byte *)(param_5 + 4 + uVar18 * 0x14);
    *pbVar2 = *pbVar2 | 1;
    *(undefined4 *)(param_5 + 0x10 + uVar18 * 0x14) = 0x25;
  }
  FUN_00906f70();
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1f0) * 0x14) = 0x13;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1f0);
  if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
     (((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
       (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))) &&
      (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')))) {
    uVar14 = *puVar25 | 0x10;
  }
  else {
    uVar14 = *puVar25 & 0xffffffef;
  }
  *puVar25 = uVar14;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 500) * 0x14) = 0x14;
  uVar18 = (ulong)*(uint *)(param_5 + 500);
  if ((((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
      ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
       (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) &&
     (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')) {
    uVar14 = *puVar25 | 0x20;
  }
  else {
    uVar14 = *puVar25 & 0xffffffdf;
  }
  *puVar25 = uVar14;
  lVar20 = (long)param_3 * 0x20;
  if ((*(char *)(DAT_0273eb28 + 0x10 + lVar20) != '\0') && ((uVar14 & 0x10) != 0)) {
    *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1f0) * 0x14) = 0x13;
    pbVar2 = (byte *)(param_5 + 4 + (ulong)*(uint *)(param_5 + 0x1f0) * 0x14);
    *pbVar2 = *pbVar2 | 1;
  }
  if ((*(char *)(DAT_0273eb28 + 0x11 + lVar20) != '\0') && ((*(byte *)puVar25 & 0x20) != 0)) {
    *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 500) * 0x14) = 0x14;
    pbVar2 = (byte *)(param_5 + 4 + (ulong)*(uint *)(param_5 + 500) * 0x14);
    *pbVar2 = *pbVar2 | 1;
  }
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1c0) * 0x14) = 7;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1c0);
  if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
     (((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
       (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))) &&
      (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')))) {
    uVar14 = *(uint *)(param_6 + 0x20) | 0x800000;
  }
  else {
    uVar14 = *(uint *)(param_6 + 0x20) & 0xff7fffff;
  }
  *(uint *)(param_6 + 0x20) = uVar14;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1cc) * 0x14) = 10;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1cc);
  if ((((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
      ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
       (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) &&
     (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')) {
    uVar14 = *(uint *)(param_6 + 0x20) | 0x1000000;
  }
  else {
    uVar14 = *(uint *)(param_6 + 0x20) & 0xfeffffff;
  }
  *(uint *)(param_6 + 0x20) = uVar14;
  if (bVar27) {
    *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1cc) * 0x14) = 10;
    uVar18 = (ulong)*(uint *)(param_5 + 0x1cc);
    if ((((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) != 0) ||
        ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 != 0x25 &&
         (iVar15 != *(int *)(param_5 + 0xc + uVar18 * 0x14))))) ||
       (*(char *)(param_5 + 2 + uVar18 * 0x14) == '\0')) goto LAB_0091e7e6;
    uVar14 = *(uint *)(param_6 + 0x20) | 0x80000;
  }
  else {
LAB_0091e7e6:
    uVar14 = *(uint *)(param_6 + 0x20) & 0xfff7ffff;
  }
  *(uint *)(param_6 + 0x20) = uVar14;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1a4) * 0x14) = 0;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1a4);
  if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
     (((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
       (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))) &&
      (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')))) {
    uVar14 = *(uint *)(param_6 + 0x20) | 0x10;
  }
  else {
    uVar14 = *(uint *)(param_6 + 0x20) & 0xffffffef;
  }
  *(uint *)(param_6 + 0x20) = uVar14;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x220) * 0x14) = 0x1f;
  uVar18 = (ulong)*(uint *)(param_5 + 0x220);
  if ((((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
      ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
       (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) &&
     (*(char *)(param_5 + 2 + uVar18 * 0x14) == '\x01')) {
    uVar14 = *puVar25 | 0x400;
  }
  else {
    uVar14 = *puVar25 & 0xfffffbff;
  }
  *puVar25 = uVar14;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1b0) * 0x14) = 3;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1b0);
  if ((((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
      ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
       (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) &&
     (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')) {
    *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1d4) * 0x14) = 0xc;
    uVar18 = (ulong)*(uint *)(param_5 + 0x1d4);
    if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
       (((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
         (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))) &&
        (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')))) {
      *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1c8) * 0x14) = 9;
      uVar18 = (ulong)*(uint *)(param_5 + 0x1c8);
      if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
         (((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
           (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))) &&
          (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')))) {
        *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1f8) * 0x14) = 0x15;
        uVar18 = (ulong)*(uint *)(param_5 + 0x1f8);
        cVar7 = '\0';
        cVar6 = '\0';
        if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
           ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
            (cVar6 = '\0', iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) {
          cVar6 = *(char *)(param_5 + 2 + uVar18 * 0x14);
        }
        *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1fc) * 0x14) = 0x16;
        uVar18 = (ulong)*(uint *)(param_5 + 0x1fc);
        if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
           ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
            (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) {
          cVar7 = *(char *)(param_5 + 2 + uVar18 * 0x14);
        }
        if (cVar6 == '<') {
          *(byte *)(param_6 + 0x25) = *(byte *)(param_6 + 0x25) | 1;
        }
        if (cVar7 == '<') {
          *(byte *)(param_6 + 0x25) = *(byte *)(param_6 + 0x25) | 2;
        }
      }
    }
  }
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1a8) * 0x14) = 1;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1a8);
  if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
     (((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
       (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))) &&
      (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')))) {
    puVar21 = (undefined1 *)(lVar4 + 0x180 + lVar24);
    uVar23 = 1;
  }
  else {
    puVar21 = (undefined1 *)(lVar4 + 0x180 + lVar24);
    uVar23 = 0;
    if (*(char *)(lVar4 + 0x180 + lVar24) != '\0') {
      if (*(char *)(lVar4 + 0x181 + lVar24) == '\0') {
        uVar14 = *puVar25 | 2;
      }
      else {
        uVar14 = *puVar25 & 0xfffffffd;
      }
      *puVar25 = uVar14;
      *puVar21 = 0;
      *(undefined1 *)(lVar4 + 0x181 + lVar24) = 0;
      goto LAB_0091ea6c;
    }
  }
  *(byte *)puVar25 = *(byte *)puVar25 & 0xfd;
  *puVar21 = uVar23;
LAB_0091ea6c:
  if ((cVar5 != '\0') && (*pcVar22 != '\0')) {
    if ((*(byte *)(param_6 + 0x20) & 0x10) != 0) {
      *pcVar22 = '\0';
    }
    if ((*puVar1 != 0xffffffff) && (cVar5 = FUN_00bd6490(), cVar5 != '\0')) {
      *pcVar22 = '\0';
    }
  }
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1b0) * 0x14) = 3;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1b4) * 0x14) = 4;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1b0) * 0x14) = 3;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1b0);
  if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
     (((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
       (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))) &&
      (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')))) {
    uVar14 = *(uint *)(param_6 + 0x28) | 1;
  }
  else {
    uVar14 = *(uint *)(param_6 + 0x28) & 0xfffffffe;
  }
  *(uint *)(param_6 + 0x28) = uVar14;
  *(uint *)(param_6 + 0x28) = uVar14 | 2;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1d4) * 0x14) = 0xc;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1d4);
  if ((((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
      ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
       (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) &&
     (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')) {
    uVar14 = *(uint *)(param_6 + 0x28) | 0x10;
  }
  else {
    uVar14 = *(uint *)(param_6 + 0x28) & 0xffffffef;
  }
  *(uint *)(param_6 + 0x28) = uVar14;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1d4) * 0x14) = 0xc;
  *(byte *)(param_6 + 0x28) = *(byte *)(param_6 + 0x28) | 0x20;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1ac) * 0x14) = 2;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1ac);
  if ((((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
      ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
       (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) &&
     (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')) {
    uVar14 = *(uint *)(param_6 + 0x28) | 0x100;
  }
  else {
    uVar14 = *(uint *)(param_6 + 0x28) & 0xfffffeff;
  }
  *(uint *)(param_6 + 0x28) = uVar14;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1ac) * 0x14) = 2;
  *(byte *)(param_6 + 0x29) = *(byte *)(param_6 + 0x29) | 2;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x218) * 0x14) = 0x1d;
  uVar18 = (ulong)*(uint *)(param_5 + 0x218);
  if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
     (((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
       (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))) &&
      (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')))) {
    uVar14 = *(uint *)(param_6 + 0x28) | 0x2000;
  }
  else {
    uVar14 = *(uint *)(param_6 + 0x28) & 0xffffdfff;
  }
  *(uint *)(param_6 + 0x28) = uVar14;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x21c) * 0x14) = 0x1e;
  uVar18 = (ulong)*(uint *)(param_5 + 0x21c);
  if ((((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
      ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
       (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) &&
     (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0')) {
    uVar14 = *(uint *)(param_6 + 0x28) | 0x8000;
  }
  else {
    uVar14 = *(uint *)(param_6 + 0x28) & 0xffff7fff;
  }
  *(uint *)(param_6 + 0x28) = uVar14;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x21c) * 0x14) = 0x1e;
  *(byte *)(param_6 + 0x2a) = *(byte *)(param_6 + 0x2a) | 2;
  *(undefined4 *)(param_5 + 0xc + (ulong)*(uint *)(param_5 + 0x1ac) * 0x14) = 2;
  uVar18 = (ulong)*(uint *)(param_5 + 0x1ac);
  if (((*(byte *)(param_5 + 4 + uVar18 * 0x14) & 1) == 0) &&
     ((iVar15 = *(int *)(param_5 + 0x10 + uVar18 * 0x14), iVar15 == 0x25 ||
      (iVar15 == *(int *)(param_5 + 0xc + uVar18 * 0x14))))) {
    pcVar22 = (char *)(lVar4 + 0x17e + lVar24);
    if (*(char *)(param_5 + 2 + uVar18 * 0x14) != '\0') {
      *pcVar22 = '\x01';
      return;
    }
  }
  else {
    pcVar22 = (char *)(lVar4 + 0x17e + lVar24);
  }
  pcVar3 = (char *)(lVar4 + 0x17f + lVar24);
  if ((*pcVar22 != '\0') && (*pcVar3 == '\0')) {
    *(byte *)puVar25 = *(byte *)puVar25 | 1;
  }
  *pcVar22 = '\0';
  *pcVar3 = '\0';
  return;
}

