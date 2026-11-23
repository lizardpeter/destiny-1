
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined8
FUN_008a9cd0(long param_1,long param_2,int param_3,long param_4,long param_5,undefined8 *param_6,
            int param_7,char param_8)

{
  undefined8 uVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  char cVar5;
  char cVar6;
  undefined7 uVar14;
  undefined1 (*pauVar7) [16];
  ulong uVar8;
  long lVar9;
  undefined8 *puVar10;
  long lVar11;
  undefined8 uVar12;
  undefined8 uVar13;
  long lVar15;
  uint uVar16;
  undefined1 auVar17 [16];
  undefined1 auVar18 [16];
  undefined1 auVar19 [16];
  undefined1 auVar20 [16];
  undefined1 local_78 [16];
  undefined8 local_68;
  undefined8 uStack_60;
  undefined8 local_58;
  undefined8 uStack_50;
  undefined8 local_48;
  undefined8 uStack_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar14 = (undefined7)((ulong)local_38 >> 8);
  if (param_8 == '\0') {
    if (*(char *)(param_4 + 8) == '\0') {
      local_78 = ZEXT416(DAT_01667dac);
      local_68 = _DAT_01667dd0;
      uStack_60 = uRam0000000001667dd8;
      local_58 = _DAT_01667de0;
      uStack_50 = uRam0000000001667de8;
      local_48 = _DAT_01667df0;
      uStack_40 = uRam0000000001667df8;
      uVar16 = (int)*(uint *)(param_5 + 0x18) >> 0xd;
      lVar15 = (ulong)((uVar16 >> 0x12 | 0x3ff) & uVar16) * 0x40;
      lVar11 = *DAT_01a238a0;
      lVar9 = *(long *)(lVar11 + 0x10 + lVar15);
      uVar8 = (ulong)((*(uint *)(param_5 + 0x18) & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar15));
      lVar15 = (lVar9 + uVar8) -
               ((long)*(int *)(lVar11 + 0x34 + lVar15) & *(ulong *)(lVar9 + 8 + uVar8));
      lVar11 = *(long *)(lVar15 + 0x10);
      lVar9 = FUN_0082cb90(8);
      if (lVar9 != 0) {
        cVar5 = FUN_00820120(param_2,lVar9,(long)param_7 * 0x50 + lVar15 + 0x20 + lVar11,
                             param_4 + 0x7e8,local_78,param_4 + 0x978,
                             *(undefined8 *)(param_2 + 0x15c0));
        if (cVar5 != '\0') {
          *(byte *)(param_2 + 0x15ad) = *(byte *)(param_2 + 0x15ad) | 1;
        }
      }
    }
    else {
      pauVar7 = (undefined1 (*) [16])FUN_0082b940(param_2,0x31,0x10);
      auVar17._4_12_ = SUB1612(*pauVar7,4);
      auVar17._0_4_ = *(undefined4 *)(param_4 + 0x978);
      *pauVar7 = auVar17;
      auVar17 = vpshufd_avx(auVar17,0xe0);
      auVar18._4_12_ = auVar17._4_12_;
      auVar18._0_4_ = *(undefined4 *)(param_4 + 0x97c);
      auVar17 = vpshufd_avx(auVar18,0xe1);
      *pauVar7 = auVar17;
      auVar17 = vpshufd_avx(auVar17,0xc4);
      auVar19._4_12_ = auVar17._4_12_;
      auVar19._0_4_ = *(undefined4 *)(param_4 + 0x980);
      auVar17 = vpshufd_avx(auVar19,0xc6);
      *pauVar7 = auVar17;
      auVar17 = vpshufd_avx(auVar17,0x24);
      auVar20._4_12_ = auVar17._4_12_;
      auVar20._0_4_ = *(undefined4 *)(param_4 + 0x984);
      auVar17 = vpshufd_avx(auVar20,0x27);
      *pauVar7 = auVar17;
    }
    puVar10 = (undefined8 *)FUN_0082b940(param_2,0x4a,0x60);
    uVar13 = *(undefined8 *)(param_1 + 0x68);
    *puVar10 = *(undefined8 *)(param_1 + 0x60);
    puVar10[1] = uVar13;
    uVar13 = *(undefined8 *)(param_1 + 0x78);
    puVar10[2] = *(undefined8 *)(param_1 + 0x70);
    puVar10[3] = uVar13;
    uVar13 = *(undefined8 *)(param_1 + 0x88);
    puVar10[4] = *(undefined8 *)(param_1 + 0x80);
    puVar10[5] = uVar13;
    uVar13 = *(undefined8 *)(param_1 + 0x98);
    puVar10[6] = *(undefined8 *)(param_1 + 0x90);
    puVar10[7] = uVar13;
    uVar13 = *(undefined8 *)(param_1 + 0xa8);
    puVar10[8] = *(undefined8 *)(param_1 + 0xa0);
    puVar10[9] = uVar13;
    uVar13 = *(undefined8 *)(param_1 + 0xb8);
    puVar10[10] = *(undefined8 *)(param_1 + 0xb0);
    puVar10[0xb] = uVar13;
    pauVar7 = (undefined1 (*) [16])FUN_0082b940(param_2,8,0x80);
    uVar4 = uRam0000000001667df8;
    uVar3 = _DAT_01667df0;
    uVar2 = uRam0000000001667de8;
    uVar1 = _DAT_01667de0;
    uVar12 = uRam0000000001667dd8;
    uVar13 = _DAT_01667dd0;
    *pauVar7 = ZEXT416(DAT_01667dac);
    *(undefined8 *)pauVar7[1] = uVar13;
    *(undefined8 *)(pauVar7[1] + 8) = uVar12;
    *(undefined8 *)pauVar7[2] = uVar1;
    *(undefined8 *)(pauVar7[2] + 8) = uVar2;
    *(undefined8 *)pauVar7[3] = uVar3;
    *(undefined8 *)(pauVar7[3] + 8) = uVar4;
    uVar13 = param_6[1];
    *(undefined8 *)pauVar7[4] = *param_6;
    *(undefined8 *)(pauVar7[4] + 8) = uVar13;
    uVar13 = param_6[3];
    *(undefined8 *)pauVar7[5] = param_6[2];
    *(undefined8 *)(pauVar7[5] + 8) = uVar13;
    uVar13 = param_6[5];
    *(undefined8 *)pauVar7[6] = param_6[4];
    *(undefined8 *)(pauVar7[6] + 8) = uVar13;
    lVar11 = FUN_0082cb90(2);
    if (lVar11 != 0) {
      cVar5 = FUN_0081fd20(param_2,lVar11,*(undefined8 *)(param_2 + 0x15c0));
      if (cVar5 == '\0') {
        cVar6 = FUN_0082bd10(param_2,1,lVar11 + 0x20);
        cVar5 = '\0';
        if (cVar6 != '\0') {
          cVar5 = FUN_0082bd10(param_2,2,lVar11 + 0xb0);
        }
      }
      if (cVar5 != '\0') {
        *(byte *)(param_2 + 0x15ac) = *(byte *)(param_2 + 0x15ac) | 4;
      }
    }
    uVar13 = *(undefined8 *)(param_2 + 0x15c0);
    uVar12 = FUN_0082e420((int)*(char *)((long)param_6 + (long)param_3 + 0x80));
    FUN_007deb70(uVar13,uVar12,0);
    FUN_007dee30(*(undefined8 *)(param_2 + 0x15c0),*(undefined4 *)(param_6 + 8));
    FUN_007dec20(*(undefined8 *)(param_2 + 0x15c0),*(undefined4 *)(param_6 + 6),0,0,0);
    cVar5 = *(char *)(param_5 + 0xc);
    FUN_007dec20(*(undefined8 *)(param_2 + 0x15c0),*(undefined4 *)(param_1 + 0x50),1,0,0);
    if (cVar5 == '\0') {
      uVar13 = FUN_008ae670(*(undefined4 *)(param_1 + 0x40));
      FUN_008ad160(uVar13,param_2,2,0);
    }
    uVar13 = FUN_0083ff90(param_2,*(undefined4 *)(param_1 + 0xf0),3,0);
    uVar14 = (undefined7)((ulong)uVar13 >> 8);
    param_8 = '\x01';
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71(uVar14,param_8 != '\0');
  }
  uVar13 = thunk_FUN_012aa7f6();
  return uVar13;
}

