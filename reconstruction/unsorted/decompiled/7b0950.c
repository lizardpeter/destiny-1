
void FUN_007b0950(long param_1,undefined4 param_2,undefined8 *param_3,uint param_4,
                 undefined8 param_5,undefined4 param_6,undefined4 *param_7)

{
  undefined4 *puVar1;
  int iVar2;
  undefined *puVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  long lVar7;
  long lVar8;
  undefined8 uVar9;
  long lVar10;
  uint uVar11;
  ushort uVar12;
  long lVar13;
  long lVar14;
  bool bVar15;
  undefined4 local_198 [2];
  undefined4 local_190 [2];
  undefined4 local_188 [2];
  undefined4 local_180;
  undefined4 local_17c;
  undefined8 local_178;
  undefined4 local_16c;
  undefined8 local_168;
  undefined4 local_15c;
  undefined1 local_158 [288];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar7 = FUN_007642b0();
  lVar8 = FUN_0034e610();
  if (((*(char *)(lVar8 + 0xd) != '\0') && (*(int *)(param_1 + 0x27a0) != 0x28)) && (lVar7 != 0)) {
    local_15c = 0xffffffff;
    local_168 = 0;
    local_16c = 0xffffffff;
    local_178 = 0;
    FUN_0066bb40(param_4,&local_168,&local_178,&local_15c,&local_16c);
    if (param_4 != 0xffffffff) {
      local_17c = 0xffffffff;
      local_180 = 0xffffffff;
      local_188[0] = 0xffffffff;
      local_190[0] = 0xffffffff;
      local_198[0] = 0xffffffff;
      lVar13 = (ulong)((param_4 & 0x1fff) * DAT_02692230) + DAT_02692228;
      FUN_0066bc30(lVar13,&local_17c,&local_180,local_188,local_190,local_198);
      FUN_0066bdd0(lVar13,local_158);
      puVar3 = PTR_DAT_019b42c0;
      iVar2 = *(int *)(param_1 + 0x27a0);
      *(int *)(param_1 + 0x27a0) = iVar2 + 1;
      lVar8 = *(long *)(puVar3 + 8);
      uVar9 = FUN_000e8680(lVar8,0,0xffffffff);
      lVar14 = (long)iVar2 * 400;
      puVar1 = (undefined4 *)(param_1 + 0x27a8 + lVar14);
      thunk_FUN_012aa986(puVar1,0,uVar9);
      uVar12 = *(ushort *)(lVar8 + 0x1c) & 0x78;
      bVar15 = uVar12 != 0;
      if (uVar12 == 0) {
        uVar11 = *(uint *)(lVar8 + 0x20);
        if ((*(ushort *)(lVar8 + 0x1c) & 0x40) != 0) {
          lVar10 = FUN_000e8a90(lVar8,puVar1);
          if (lVar10 == 0) {
            uVar11 = uVar11 | 0x5488bf;
          }
          else {
            uVar11 = *(uint *)(lVar10 + 0x20) & 0x5488bf | uVar11;
          }
        }
        bVar15 = (uVar11 & 0xc08070) != 0;
      }
      if (bVar15) {
        FUN_000e6730(lVar8,puVar1,0,0xffffffff,0);
      }
      *puVar1 = param_2;
      uVar9 = *param_3;
      *(undefined8 *)(param_1 + 0x27b8 + lVar14) = param_3[1];
      *(undefined8 *)(param_1 + 0x27b0 + lVar14) = uVar9;
      uVar6 = FUN_002a2d90(lVar7);
      *(undefined4 *)(param_1 + 0x27c0 + lVar14) = uVar6;
      FUN_0066df00(param_5,param_1 + 0x2924 + lVar14);
      *(undefined4 *)(param_1 + 0x2930 + lVar14) = param_6;
      lVar7 = FUN_0034e610();
      if (*(char *)(lVar7 + 3) != '\0') {
        FUN_0066dfb0(&DAT_000027c8 + lVar14 + param_1);
      }
      uVar9 = local_178;
      lVar7 = FUN_0034e610();
      if (*(char *)(lVar7 + 6) != '\0') {
        FUN_0066e020(lVar13,uVar9,param_1 + 0x27f0 + lVar14);
      }
      uVar9 = local_168;
      lVar7 = FUN_0034e610();
      if (*(char *)(lVar7 + 7) != '\0') {
        FUN_0066e100(uVar9,param_1 + 0x2808 + lVar14);
      }
      uVar4 = local_15c;
      uVar9 = local_178;
      uVar6 = local_17c;
      lVar7 = FUN_0034e610();
      if (*(char *)(lVar7 + 8) != '\0') {
        *(undefined4 *)(param_1 + 0x2840 + lVar14) = uVar6;
        FUN_0066e850(uVar4,uVar9,param_4,param_1 + 0x2838 + lVar14);
      }
      uVar6 = local_15c;
      lVar7 = FUN_0034e610();
      if (*(char *)(lVar7 + 9) != '\0') {
        FUN_0066ea10(uVar6,param_1 + 0x2854 + lVar14);
      }
      uVar9 = local_168;
      lVar7 = FUN_0034e610();
      if (*(char *)(lVar7 + 10) != '\0') {
        FUN_0066e140(uVar9,lVar13,local_158,param_1 + 0x285c + lVar14);
      }
      uVar5 = local_180;
      uVar4 = local_188[0];
      uVar6 = local_190[0];
      lVar7 = FUN_0034e610();
      if (*(char *)(lVar7 + 0xb) != '\0') {
        FUN_0066e740(uVar5,uVar4,uVar6,param_1 + 0x28a4 + lVar14);
      }
      thunk_FUN_0066d4b0(param_4,param_1 + 0x291c + lVar14);
      *(undefined4 *)(param_1 + 0x2920 + lVar14) = *param_7;
    }
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

