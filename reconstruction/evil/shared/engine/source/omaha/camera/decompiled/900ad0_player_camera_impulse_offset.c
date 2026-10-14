
undefined8
FUN_00900ad0(float param_1,int param_2,undefined8 param_3,undefined8 param_4,undefined8 param_5)

{
  uint uVar1;
  long lVar2;
  uint *puVar3;
  char cVar4;
  short sVar5;
  int iVar6;
  ulong uVar7;
  undefined8 uVar8;
  long lVar9;
  long lVar10;
  float *pfVar11;
  uint *puVar12;
  long lVar13;
  float fVar14;
  float fVar15;
  float fVar16;
  ulong uVar17;
  undefined1 auVar18 [16];
  undefined1 auVar19 [64];
  float fVar20;
  undefined1 auVar21 [16];
  float fVar22;
  float local_50;
  undefined1 local_4c;
  float local_48 [4];
  long local_38;
  undefined1 extraout_var [56];
  
  local_38 = *DAT_01a1f100;
  local_48[2] = 0.0;
  local_48[3] = 0.0;
  local_48[0] = 0.0;
  local_48[1] = 0.0;
  cVar4 = FUN_00906f70();
  local_4c = 0;
  local_50 = 0.0;
  if (cVar4 != '\0') {
    fVar14 = 0.0;
    fVar22 = 0.0;
    fVar20 = 0.0;
    local_50 = 0.0;
    goto LAB_00900d1a;
  }
  iVar6 = FUN_00923110(param_2);
  fVar14 = DAT_0166afc0;
  if (iVar6 == -1) {
LAB_00900b6e:
    fVar15 = DAT_0166afc0 / fVar14;
  }
  else {
    sVar5 = FUN_00bd35b0(iVar6);
    fVar14 = (float)FUN_00bd3740(iVar6,(int)sVar5);
    fVar15 = DAT_0166afc0;
    if (DAT_0166afc4 < fVar14) goto LAB_00900b6e;
  }
  fVar16 = (float)FUN_00591b80();
  puVar3 = DAT_0273da50;
  fVar14 = 0.0;
  fVar22 = 0.0;
  fVar20 = 0.0;
  if (param_2 == 0) {
    local_4c = 0;
    lVar13 = 0;
    puVar12 = DAT_0273da50;
    do {
      uVar1 = *puVar12;
      if (uVar1 != 0xffffffff) {
        lVar9 = (ulong)(((uint)((int)uVar1 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar1 >> 0xd) * 0x40;
        auVar18 = ZEXT416(puVar3[lVar13 + 0xa8]);
        lVar10 = *DAT_01a238a0;
        lVar2 = *(long *)(lVar10 + 0x10 + lVar9);
        uVar7 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar10 + 0x30 + lVar9));
        lVar10 = (lVar2 + uVar7) -
                 ((long)*(int *)(lVar10 + 0x34 + lVar9) & *(ulong *)(lVar2 + 8 + uVar7));
        pfVar11 = local_48;
        if ((char)puVar12[0x13] == '\0') {
          pfVar11 = local_48 + 2;
        }
        fVar14 = *(float *)(lVar10 + 8) * (float)puVar12[6];
        if (*(char *)((long)puVar12 + 0x51) != '\0') {
          auVar19._0_8_ = thunk_FUN_012ab996(puVar3[lVar13 + 0xa8],fVar14);
          auVar19._8_56_ = extraout_var;
          auVar18 = auVar19._0_16_;
        }
        local_4c = 1;
        if ((DAT_0166afcc <= fVar14) && (auVar18._0_4_ <= fVar14)) {
          auVar21._0_4_ = auVar18._0_4_ / fVar14;
          auVar21._4_12_ = auVar18._4_12_;
          uVar7 = auVar21._0_8_;
          if (auVar21._0_4_ < 0.0) {
            uVar7 = 0;
          }
          uVar17 = (ulong)(uint)DAT_0166afc0;
          if ((float)uVar7 + DAT_0166afc8 < 0.0) {
            uVar17 = uVar7;
          }
          fVar14 = (float)FUN_00239650(uVar17,lVar10 + 0x18);
          fVar14 = fVar15 * (param_1 / fVar16) * fVar14 * (float)puVar12[5] * (float)puVar12[0x12];
          *pfVar11 = fVar14 * (float)puVar12[3] + *pfVar11;
          pfVar11[1] = fVar14 * (float)puVar12[4] + pfVar11[1];
        }
      }
      puVar12 = puVar12 + 0x15;
      lVar13 = lVar13 + 1;
    } while ((int)lVar13 != 8);
    fVar14 = (float)local_48._0_8_;
    local_50 = local_48[1];
    fVar22 = (float)local_48._8_8_;
    fVar20 = local_48[3];
  }
LAB_00900d1a:
  FUN_000ab3c0(fVar22 + fVar14,fVar20 + local_50,param_3);
  FUN_000ab3c0(fVar14,local_50,param_4);
  FUN_000aa760(0,0,param_5);
  if (*DAT_01a1f100 != local_38) {
    uVar8 = thunk_FUN_012aa7f6();
    return uVar8;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),local_4c);
}

