
void FUN_007dd6a0(long *param_1,long param_2,undefined8 param_3,uint *param_4)

{
  float fVar1;
  uint uVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  long lVar6;
  float fVar7;
  char cVar8;
  ulong uVar9;
  long *plVar10;
  uint *puVar11;
  undefined8 uVar12;
  uint *puVar13;
  undefined4 uVar14;
  uint *puVar15;
  char *pcVar16;
  uint *puVar17;
  ulong uVar18;
  char *pcVar19;
  long lVar20;
  uint *puVar21;
  int iVar22;
  int iVar23;
  long *plVar24;
  uint *puVar25;
  float fVar26;
  undefined1 auVar27 [16];
  undefined1 auVar28 [16];
  undefined1 auVar29 [16];
  float fVar30;
  float fVar31;
  float fVar32;
  long local_60;
  float local_50;
  float local_4c;
  float local_48;
  float local_44;
  float local_40;
  float local_3c;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  param_1[0xb] = param_2;
  plVar10 = param_1 + 10;
  if (param_4 == (uint *)0x0) {
    FUN_007dc270(param_1,0);
    uVar9 = (ulong)*(uint *)(*param_1 + 0xb4);
    lVar20 = uVar9 * 0xe60;
    param_1[10] = (long)(param_1 + uVar9 * 0x1cc + 0xc);
    *(undefined1 *)((long)param_1 + lVar20 + 0x22b) = 0xff;
    *(undefined2 *)((long)param_1 + lVar20 + 0x229) = 0xffff;
    *(undefined4 *)((long)param_1 + lVar20 + 0x225) = 0xffffffff;
    *(undefined1 *)((long)param_1 + lVar20 + 0x152) = 0xff;
    *(undefined2 *)(param_1 + uVar9 * 0x1cc + 0x2a) = 0xffff;
    param_1[uVar9 * 0x1cc + 0x29] = -1;
    param_1[uVar9 * 0x1cc + 0x28] = -1;
    param_1[uVar9 * 0x1cc + 0x27] = -1;
    param_1[uVar9 * 0x1cc + 0x26] = -1;
    thunk_FUN_012aa986((long)param_1 + lVar20 + 0x15a,0xff,0xc4);
    *(undefined4 *)(param_2 + 0x20) = *(undefined4 *)(*param_1 + 0xb4);
    FUN_007ef9c0(&DAT_026e4840,plVar10);
    goto LAB_007de32d;
  }
  FUN_007dc270(param_1,1);
  param_1[10] = (long)(param_1 + (ulong)param_4[0x5e1] * 0x1cc + 0xc);
  *(uint *)(param_2 + 0x20) = param_4[0x5e1];
  lVar20 = param_1[10];
  *(uint **)(lVar20 + 200) = param_4 + 0x8ce;
  *(undefined1 *)(lVar20 + 0xd6) = *(undefined1 *)((long)param_4 + 0x179e);
  *(short *)(lVar20 + 0xd4) = (short)param_4[0x5e7];
  *(uint *)(lVar20 + 0xd0) = param_4[0x5e6];
  *(undefined1 *)(lVar20 + 0xdd) = *(undefined1 *)((long)param_4 + 0x17a5);
  *(undefined2 *)(lVar20 + 0xdb) = *(undefined2 *)((long)param_4 + 0x17a3);
  *(undefined4 *)(lVar20 + 0xd7) = *(undefined4 *)((long)param_4 + 0x179f);
  *(char *)(lVar20 + 0xe4) = (char)param_4[0x5eb];
  *(undefined2 *)(lVar20 + 0xe2) = *(undefined2 *)((long)param_4 + 0x17aa);
  *(undefined4 *)(lVar20 + 0xde) = *(undefined4 *)((long)param_4 + 0x17a6);
  *(undefined1 *)(lVar20 + 0xeb) = *(undefined1 *)((long)param_4 + 0x17b3);
  *(undefined2 *)(lVar20 + 0xe9) = *(undefined2 *)((long)param_4 + 0x17b1);
  *(undefined4 *)(lVar20 + 0xe5) = *(undefined4 *)((long)param_4 + 0x17ad);
  *(undefined1 *)(lVar20 + 0xf2) = *(undefined1 *)((long)param_4 + 0x17ba);
  *(short *)(lVar20 + 0xf0) = (short)param_4[0x5ee];
  *(uint *)(lVar20 + 0xec) = param_4[0x5ed];
  *(char *)(lVar20 + 0x100) = (char)param_4[0x5f2];
  *(undefined2 *)(lVar20 + 0xfe) = *(undefined2 *)((long)param_4 + 0x17c6);
  *(undefined4 *)(lVar20 + 0xfa) = *(undefined4 *)((long)param_4 + 0x17c2);
  thunk_FUN_012aa7c6(lVar20 + 0x101,(long)param_4 + 0x17c9,0x70);
  *(undefined2 *)(lVar20 + 0x17d) = *(undefined2 *)((long)param_4 + 0x1845);
  *(undefined4 *)(lVar20 + 0x179) = *(undefined4 *)((long)param_4 + 0x1841);
  *(undefined8 *)(lVar20 + 0x171) = *(undefined8 *)((long)param_4 + 0x1839);
  *(undefined2 *)(lVar20 + 0x18b) = *(undefined2 *)((long)param_4 + 0x1853);
  *(undefined4 *)(lVar20 + 0x187) = *(undefined4 *)((long)param_4 + 0x184f);
  *(undefined8 *)(lVar20 + 0x17f) = *(undefined8 *)((long)param_4 + 0x1847);
  *(undefined4 *)(lVar20 + 0x1a5) = *(undefined4 *)((long)param_4 + 0x186d);
  *(undefined8 *)(lVar20 + 0x19d) = *(undefined8 *)((long)param_4 + 0x1865);
  uVar12 = *(undefined8 *)((long)param_4 + 0x1855);
  *(undefined8 *)(lVar20 + 0x195) = *(undefined8 *)((long)param_4 + 0x185d);
  *(undefined8 *)(lVar20 + 0x18d) = uVar12;
  *(undefined1 *)(lVar20 + 0x1bd) = *(undefined1 *)((long)param_4 + 0x1885);
  *(undefined4 *)(lVar20 + 0x1b9) = *(undefined4 *)((long)param_4 + 0x1881);
  uVar12 = *(undefined8 *)((long)param_4 + 0x1871);
  *(undefined8 *)(lVar20 + 0x1b1) = *(undefined8 *)((long)param_4 + 0x1879);
  *(undefined8 *)(lVar20 + 0x1a9) = uVar12;
  *(undefined1 *)(lVar20 + 0x1cb) = *(undefined1 *)((long)param_4 + 0x1893);
  *(undefined2 *)(lVar20 + 0x1c9) = *(undefined2 *)((long)param_4 + 0x1891);
  *(undefined4 *)(lVar20 + 0x1c5) = *(undefined4 *)((long)param_4 + 0x188d);
  FUN_007ef9c0(&DAT_026e4840,plVar10);
  if (param_1[10] != 0) {
    uVar2 = param_4[0x4a];
    FUN_00f8f0e0(param_1[10],0,param_4 + 0x13);
    uVar12 = *(undefined8 *)(param_4 + 0x1b);
    *(uint *)((long)param_1 + 0x270c) = param_4[0x1d];
    *(undefined8 *)((long)param_1 + 0x2704) = uVar12;
    *(undefined8 *)((long)param_1 + 0x26fc) = *(undefined8 *)(param_4 + 0x19);
    *(undefined8 *)((long)param_1 + 0x26f4) = *(undefined8 *)(param_4 + 0x17);
    uVar12 = *(undefined8 *)(param_4 + 0x13);
    *(undefined8 *)((long)param_1 + 0x26ec) = *(undefined8 *)(param_4 + 0x15);
    *(undefined8 *)((long)param_1 + 0x26e4) = uVar12;
    *(uint *)((long)param_1 + 0x27c4) = uVar2;
    if (param_1[10] != 0) {
      uVar2 = param_4[0x4b];
      FUN_00f8f0e0(param_1[10],1,param_4 + 0x1e);
      lVar20 = *(long *)(param_4 + 0x26);
      *(uint *)(param_1 + 0x4e7) = param_4[0x28];
      param_1[0x4e6] = lVar20;
      param_1[0x4e5] = *(long *)(param_4 + 0x24);
      param_1[0x4e4] = *(long *)(param_4 + 0x22);
      lVar20 = *(long *)(param_4 + 0x1e);
      param_1[0x4e3] = *(long *)(param_4 + 0x20);
      param_1[0x4e2] = lVar20;
      *(uint *)(param_1 + 0x4f9) = uVar2;
      if (param_1[10] != 0) {
        uVar2 = param_4[0x4c];
        FUN_00f8f0e0(param_1[10],2,param_4 + 0x29);
        uVar12 = *(undefined8 *)(param_4 + 0x31);
        *(uint *)((long)param_1 + 0x2764) = param_4[0x33];
        *(undefined8 *)((long)param_1 + 0x275c) = uVar12;
        *(undefined8 *)((long)param_1 + 0x2754) = *(undefined8 *)(param_4 + 0x2f);
        *(undefined8 *)((long)param_1 + 0x274c) = *(undefined8 *)(param_4 + 0x2d);
        uVar12 = *(undefined8 *)(param_4 + 0x29);
        *(undefined8 *)((long)param_1 + 0x2744) = *(undefined8 *)(param_4 + 0x2b);
        *(undefined8 *)((long)param_1 + 0x273c) = uVar12;
        *(uint *)((long)param_1 + 0x27cc) = uVar2;
        if (param_1[10] != 0) {
          uVar2 = param_4[0x4d];
          FUN_00f8f0e0(param_1[10],3,param_4 + 0x34);
          lVar20 = *(long *)(param_4 + 0x3c);
          *(uint *)(param_1 + 0x4f2) = param_4[0x3e];
          param_1[0x4f1] = lVar20;
          param_1[0x4f0] = *(long *)(param_4 + 0x3a);
          param_1[0x4ef] = *(long *)(param_4 + 0x38);
          lVar20 = *(long *)(param_4 + 0x34);
          param_1[0x4ee] = *(long *)(param_4 + 0x36);
          param_1[0x4ed] = lVar20;
          *(uint *)(param_1 + 0x4fa) = uVar2;
          if (param_1[10] != 0) {
            FUN_00f7eec0(param_1[10],param_4 + 0x4f);
            lVar20 = *(long *)(param_4 + 0x57);
            lVar6 = *(long *)(param_4 + 0x59);
            *(uint *)(param_1 + 0x4dc) = param_4[0x5b];
            param_1[0x4db] = lVar6;
            param_1[0x4da] = lVar20;
            param_1[0x4d9] = *(long *)(param_4 + 0x55);
            param_1[0x4d8] = *(long *)(param_4 + 0x53);
            lVar20 = *(long *)(param_4 + 0x4f);
            param_1[0x4d7] = *(long *)(param_4 + 0x51);
            param_1[0x4d6] = lVar20;
          }
        }
      }
    }
  }
  *(uint *)((long)param_1 + 0x25ac) = param_4[0x60];
  *(uint *)(param_1 + 0x4b6) = param_4[0x61];
  *(undefined1 *)((long)param_1 + 0x26) = *(undefined1 *)((long)param_4 + 0x49);
  fVar7 = DAT_0165fe48;
  local_3c = DAT_0165fe44;
  fVar30 = DAT_0165fe40;
  *(uint *)(param_1 + 0x4b7) = param_4[0xb];
  *(uint *)(param_1 + 0x4bd) = param_4[0x11];
  *(char *)((long)param_1 + 0x24) = (char)param_4[0x12];
  *(uint *)(param_1 + 0x4ba) = param_4[0x62];
  *(uint *)((long)param_1 + 0x25d4) = param_4[99];
  *(uint *)(param_1 + 0x4bb) = param_4[100];
  *(uint *)((long)param_1 + 0x25dc) = param_4[0x65];
  *(uint *)(param_1 + 0x4bc) = param_4[0x66];
  *(uint *)((long)param_1 + 0x25e4) = param_4[0x67];
  uVar2 = param_4[2];
  local_44 = (float)uVar2 * fVar30;
  uVar3 = param_4[1];
  fVar31 = (float)param_4[4];
  fVar1 = (float)param_4[5];
  uVar4 = param_4[3];
  fVar32 = (float)uVar4;
  local_40 = fVar32 * fVar7;
  fVar26 = fVar1 - fVar31;
  local_48 = fVar31 / fVar26;
  local_3c = local_3c / fVar26;
  local_4c = (float)uVar3 + fVar32 * fVar30;
  local_50 = (float)*param_4 + local_44;
  *(uint *)(param_1 + 0x4af) = *param_4;
  *(uint *)((long)param_1 + 0x257c) = uVar3;
  *(uint *)(param_1 + 0x4b0) = uVar2;
  *(uint *)((long)param_1 + 0x2584) = uVar4;
  *(float *)(param_1 + 0x4b1) = fVar31;
  *(float *)((long)param_1 + 0x258c) = fVar1;
  FUN_00f80340(param_1[10],0,&local_44,&local_50);
  uVar2 = param_4[9];
  uVar3 = param_4[8];
  uVar4 = param_4[7];
  uVar5 = param_4[6];
  FUN_00f80440(param_1[10],uVar5,uVar4,uVar3,uVar2);
  fVar31 = (float)uVar5 + (float)uVar3 * fVar30;
  auVar28 = vroundss_avx(ZEXT416((uint)DAT_0165fe4c),ZEXT416((uint)(fVar31 * DAT_0165fe4c + fVar30))
                         ,1);
  fVar1 = (float)uVar4 + (float)uVar2 * fVar30;
  auVar27 = ZEXT416((uint)(fVar1 * DAT_0165fe4c + fVar30));
  auVar29 = vroundss_avx(auVar27,auVar27,1);
  FUN_00f7ebb0(param_1[10],(int)auVar28._0_4_,(int)auVar29._0_4_);
  auVar27 = vandps_avx(ZEXT416((uint)((float)uVar3 * fVar30)),ZEXT416(DAT_0165fe00));
  fVar26 = auVar27._0_4_;
  fVar32 = (float)((int)auVar28._0_4_ << 4);
  auVar27 = vandps_avx(ZEXT416((uint)((float)uVar2 * fVar7)),ZEXT416(DAT_0165fe00));
  fVar30 = auVar27._0_4_;
  auVar27 = vminss_avx(ZEXT416((uint)(((fVar31 - fVar26) - fVar32) + DAT_0165fe54)),
                       ZEXT416((uint)(fVar32 + ((DAT_0165fe50 - fVar26) - fVar31))));
  auVar28._0_4_ = auVar27._0_4_ / fVar26;
  auVar28._4_12_ = auVar27._4_12_;
  fVar31 = (float)((int)auVar29._0_4_ << 4);
  auVar27 = vminss_avx(ZEXT416((uint)(((fVar1 - fVar30) - fVar31) + DAT_0165fe54)),
                       ZEXT416((uint)(fVar31 + ((DAT_0165fe50 - fVar30) - fVar1))));
  auVar29._0_4_ = auVar27._0_4_ / fVar30;
  auVar29._4_12_ = auVar27._4_12_;
  FUN_00f7ec30(auVar28._0_8_,auVar29._0_8_,param_1[10]);
  *(uint *)(param_1 + 0x4b2) = uVar5;
  *(uint *)((long)param_1 + 0x2594) = uVar4;
  *(uint *)(param_1 + 0x4b3) = uVar3;
  *(uint *)((long)param_1 + 0x259c) = uVar2;
  if (param_1[10] != 0) {
    uVar2 = param_4[0x11];
    if ((*(uint *)(param_1 + 0x4bd) != uVar2) || (*(uint *)(param_1 + 0x4b7) != param_4[0xb])) {
      FUN_007e0de0(param_1,param_4[0xb],uVar2);
      *(uint *)(param_1 + 0x4bd) = uVar2;
    }
  }
  FUN_007de4a0(param_1,param_4[10]);
  FUN_007de590(param_1,param_4[0xd]);
  FUN_007de640(param_1,param_4[0xc]);
  cVar8 = (char)param_4[0xe];
  if (*(char *)((long)param_1 + 0x25c4) != cVar8) {
    fVar31 = (float)param_4[0x10];
    fVar1 = (float)param_4[0xf];
    if ((*(float *)(param_1 + 0x4b9) == fVar1) && (!NAN(*(float *)(param_1 + 0x4b9)) && !NAN(fVar1))
       ) {
      if ((*(float *)((long)param_1 + 0x25cc) == fVar31) &&
         (!NAN(*(float *)((long)param_1 + 0x25cc)) && !NAN(fVar31))) goto LAB_007ddf52;
    }
    FUN_00f81dd0((long)param_1 + 0x25dc,cVar8);
    FUN_00f7ea80(fVar1,fVar31,param_1[10]);
    *(char *)((long)param_1 + 0x25c4) = cVar8;
    *(float *)(param_1 + 0x4b9) = fVar1;
    *(float *)((long)param_1 + 0x25cc) = fVar31;
  }
LAB_007ddf52:
  lVar20 = *plVar10;
  if (lVar20 == 0) {
    local_60 = 0xc0;
  }
  else {
    FUN_00f7f790(lVar20,0);
    FUN_00f7f840(lVar20,0);
    FUN_00f80730(lVar20,0xffff);
    FUN_00f7f7e0(lVar20,0);
    local_60 = lVar20 + 0xc0;
    FUN_00f8b500(local_60,2,0,1,0);
    uVar9 = *(ulong *)(param_4 + 0x5e);
    if (param_1[0x3a6] != uVar9) {
      if (uVar9 == 0) {
        lVar6 = param_1[10];
        uVar18 = 0;
      }
      else {
        lVar6 = param_1[10];
        uVar18 = uVar9;
      }
      FUN_00f8b8c0(lVar6 + 0xc0,uVar18);
      param_1[0x3a6] = uVar9;
      uVar9 = *(ulong *)(param_4 + 0x5e);
    }
    if (uVar9 < 2) {
      FUN_00f8b8c0(local_60,0);
    }
    pcVar16 = *(char **)(param_4 + 0x5c);
    if ((char *)param_1[0x3a5] != pcVar16) {
      if (pcVar16 == (char *)0x0) {
        lVar6 = param_1[10];
        pcVar19 = (char *)0x0;
        uVar14 = 0;
        uVar12 = 0;
      }
      else {
        lVar6 = param_1[10];
        uVar12 = *(undefined8 *)(pcVar16 + 8);
        uVar14 = *(undefined4 *)pcVar16;
        pcVar19 = pcVar16 + 0x14;
      }
      FUN_00f8b790(lVar6 + 0xc0,pcVar19,uVar14,uVar12);
      param_1[0x3a5] = (long)pcVar16;
      pcVar16 = *(char **)(param_4 + 0x5c);
    }
    if (pcVar16 < s__libexec_ld_elf_so_1_00000000 + 2) {
      FUN_00f8b790(local_60,0,0,0);
    }
    *(int *)(lVar20 + 0x3a8) = (int)param_1[0x4be];
    FUN_00f7fe20(lVar20);
    uVar2 = param_4[0x68];
    if (*(uint *)(param_1 + 0x4be) != uVar2) {
      lVar20 = param_1[10];
      *(uint *)(lVar20 + 0x3a8) = uVar2;
      FUN_00f7fe20(lVar20,uVar2);
      if ((uVar2 != 0xad) && (uVar2 != 0xb0)) {
        FUN_00f7fa90(param_1[10],0,0);
      }
      *(uint *)(param_1 + 0x4be) = uVar2;
    }
  }
  plVar10 = param_1 + 0x43f;
  puVar13 = param_4 + 0x69;
  puVar15 = param_4 + 0x245;
  param_4 = param_4 + 0x229;
  iVar23 = 0;
  do {
    iVar22 = 0;
    puVar11 = param_4;
    puVar17 = puVar13;
    plVar24 = plVar10;
    puVar25 = puVar15;
    do {
      if ((char)*puVar11 == '\0') {
        lVar20 = local_60;
        puVar21 = (uint *)0x0;
LAB_007de245:
        FUN_00f8b410(lVar20,iVar23,iVar22,1,puVar21);
      }
      else if (puVar17 != (uint *)*plVar24) {
        *plVar24 = (long)puVar17;
        lVar20 = param_1[10] + 0xc0;
        puVar21 = puVar17;
        goto LAB_007de245;
      }
      if ((char)puVar11[0x39c] == '\0') {
        FUN_00f8afd0(local_60,iVar23,iVar22,1);
      }
      else if (puVar25 != (uint *)plVar24[-0x70]) {
        cVar8 = FUN_00f84710(puVar25);
        puVar21 = (uint *)&DAT_026df2b4;
        if (cVar8 != '\0') {
          puVar21 = puVar25;
        }
        FUN_00f8afd0(param_1[10] + 0xc0,iVar23,iVar22,1);
        plVar24[-0x70] = (long)puVar21;
      }
      plVar24 = plVar24 + 1;
      puVar17 = puVar17 + 4;
      puVar25 = puVar25 + 8;
      puVar11 = (uint *)((long)puVar11 + 1);
      iVar22 = iVar22 + 1;
    } while (iVar22 != 0x10);
    plVar10 = plVar10 + 0x10;
    puVar13 = puVar13 + 0x40;
    puVar15 = puVar15 + 0x80;
    param_4 = param_4 + 4;
    iVar23 = iVar23 + 1;
  } while (iVar23 != 7);
LAB_007de32d:
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

