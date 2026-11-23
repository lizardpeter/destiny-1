
void FUN_0073fd50(long param_1,long param_2,long param_3)

{
  undefined *puVar1;
  char cVar2;
  uint uVar3;
  uint uVar4;
  undefined4 uVar5;
  long lVar6;
  ulong uVar7;
  long lVar8;
  undefined8 uVar9;
  long lVar10;
  long lVar11;
  uint uVar12;
  uint uVar13;
  bool bVar14;
  long local_320;
  long local_318;
  undefined8 local_310;
  undefined8 local_308;
  undefined4 local_300;
  undefined1 local_2f8;
  long local_2f0;
  long local_2e8;
  undefined8 local_2e0;
  undefined8 local_2d8;
  undefined4 local_2d0;
  undefined1 local_2c8;
  undefined4 local_2bc;
  long local_2b8;
  long local_2b0;
  undefined8 local_2a8;
  undefined8 local_2a0;
  undefined4 local_298;
  undefined1 local_290;
  long local_288;
  long local_280;
  undefined8 local_278;
  undefined8 local_270;
  undefined4 local_268;
  undefined1 local_260;
  undefined1 local_258 [24];
  uint local_240;
  long local_238;
  undefined1 local_228 [24];
  uint local_210;
  long local_208;
  undefined1 local_1f8 [24];
  uint local_1e0;
  long local_1d8;
  undefined1 local_1c8 [24];
  uint local_1b0;
  long local_1a8;
  undefined1 local_198 [24];
  uint local_180;
  long local_178;
  undefined2 local_168;
  undefined2 local_166;
  undefined2 local_164;
  undefined1 local_160 [24];
  undefined4 local_148;
  undefined4 local_128;
  undefined4 local_108;
  undefined4 local_e8;
  undefined4 local_c8;
  undefined4 local_a8;
  undefined4 local_88;
  undefined4 local_68;
  undefined4 local_60;
  undefined4 local_5c;
  undefined4 local_58;
  undefined4 local_54;
  undefined4 local_50;
  undefined4 local_4c;
  undefined4 local_48;
  undefined4 local_44;
  undefined4 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_0104f3a0(param_1 + 0x158,param_3);
  *(byte *)(param_1 + 0x141b) = *(byte *)(param_1 + 0x141b) | 8;
  puVar1 = PTR_DAT_0191a938;
  uVar12 = *(uint *)(param_1 + 0x2c);
  lVar6 = FUN_0052b030();
  cVar2 = FUN_00337fe0((ulong)((uVar12 & 0x1fff) * DAT_02692230) + DAT_02692228,
                       *(undefined4 *)puVar1,local_1f8,0);
  if (cVar2 != '\0') {
    lVar10 = (ulong)(((uint)((int)local_1e0 >> 0xd) >> 0x12 | 0x3ff) & (int)local_1e0 >> 0xd) * 0x40
    ;
    lVar11 = *DAT_01a238a0;
    lVar8 = *(long *)(lVar11 + 0x10 + lVar10);
    uVar7 = (ulong)((local_1e0 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar10));
    uVar12 = *(uint *)(local_1d8 + 0x24 +
                      ((lVar8 + uVar7) -
                      ((long)*(int *)(lVar11 + 0x34 + lVar10) & *(ulong *)(lVar8 + 8 + uVar7))));
    if ((uVar12 != 0xffffffff) && (lVar6 != 0)) {
      lVar10 = (ulong)(((uint)((int)uVar12 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar12 >> 0xd) * 0x40;
      lVar11 = *DAT_01a238a0;
      lVar8 = *(long *)(lVar11 + 0x10 + lVar10);
      uVar7 = (ulong)((uVar12 & 0x1fff) * *(int *)(lVar11 + 0x30 + lVar10));
      lVar11 = (lVar8 + uVar7) -
               ((long)*(int *)(lVar11 + 0x34 + lVar10) & *(ulong *)(lVar8 + 8 + uVar7));
      if (((ulong)(long)*(char *)(param_2 + 8) < 3) &&
         (*(int *)(lVar6 + 0x148 + (long)*(char *)(param_2 + 8) * 4) != -1)) {
        FUN_00316f10(lVar11);
      }
      if (((ulong)(long)*(char *)(param_2 + 9) < 2) &&
         (*(int *)(lVar6 + 0x154 + (long)*(char *)(param_2 + 9) * 4) != -1)) {
        FUN_00316f10(lVar11);
      }
      if (((ulong)(long)*(char *)(param_2 + 10) < 4) &&
         (*(int *)(lVar6 + 0x138 + (long)*(char *)(param_2 + 10) * 4) != -1)) {
        FUN_00316f10(lVar11);
      }
      if (((ulong)(long)*(char *)(param_3 + 8) < 3) &&
         (*(int *)(lVar6 + 0x148 + (long)*(char *)(param_3 + 8) * 4) != -1)) {
        FUN_00316bd0(lVar11);
      }
      if (((ulong)(long)*(char *)(param_3 + 9) < 2) &&
         (*(int *)(lVar6 + 0x154 + (long)*(char *)(param_3 + 9) * 4) != -1)) {
        FUN_00316bd0(lVar11);
      }
      if (((ulong)(long)*(char *)(param_3 + 10) < 4) &&
         (*(int *)(lVar6 + 0x138 + (long)*(char *)(param_3 + 10) * 4) != -1)) {
        FUN_00316bd0(lVar11);
      }
    }
  }
  uVar12 = *(uint *)(param_1 + 0xb0);
  if (uVar12 != 0xffffffff) {
    lVar8 = (ulong)(((uint)((int)uVar12 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar12 >> 0xd) * 0x40;
    lVar6 = *DAT_01a238a0;
    lVar11 = *(long *)(lVar6 + 0x10 + lVar8);
    uVar7 = (ulong)((uVar12 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
    lVar6 = (lVar11 + uVar7) -
            ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar11 + 8 + uVar7));
    FUN_006f1fc0(lVar6,*(undefined1 *)(param_3 + 9));
    FUN_006f2030(lVar6,*(undefined1 *)(param_3 + 8));
    FUN_006f20a0(lVar6,*(undefined1 *)(param_3 + 10));
  }
  uVar12 = *(uint *)(param_1 + 0x130);
  if (uVar12 != 0xffffffff) {
    uVar13 = *(uint *)(param_1 + 0x2c);
    uVar4 = *(uint *)(&DAT_0267fe58 + (ulong)(uVar13 >> 5 & 0xff) * 4);
    local_260 = 0;
    lVar8 = (ulong)(((uint)((int)uVar12 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar12 >> 0xd) * 0x40;
    uVar3 = (int)*(uint *)(param_1 + 0x128) >> 0xd;
    lVar10 = (ulong)((uVar3 >> 0x12 | 0x3ff) & uVar3) * 0x40;
    lVar6 = *DAT_01a238a0;
    lVar11 = *(long *)(lVar6 + 0x10 + lVar10);
    uVar7 = (ulong)((*(uint *)(param_1 + 0x128) & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar10));
    local_288 = (lVar11 + uVar7) -
                ((long)*(int *)(lVar6 + 0x34 + lVar10) & *(ulong *)(lVar11 + 8 + uVar7));
    lVar11 = *(long *)(lVar6 + 0x10 + lVar8);
    uVar7 = (ulong)((uVar12 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
    local_280 = ((lVar11 + uVar7) -
                ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar11 + 8 + uVar7))) +
                *(long *)(param_1 + 0x138);
    local_268 = *(undefined4 *)(param_1 + 0x140);
    local_278 = *(undefined8 *)(param_1 + 0x130);
    local_270 = *(undefined8 *)(param_1 + 0x138);
    FUN_00353640(&local_288,param_3);
    FUN_00bf2ed0(&local_288,param_3,-((uVar4 >> (uVar13 & 0x1f) & 1) != 0) & 1);
    uVar12 = *(uint *)(param_1 + 0x98);
    if (uVar12 != 0xffffffff) {
      local_290 = 0;
      uVar4 = (int)*(uint *)(param_1 + 0x90) >> 0xd;
      lVar6 = *DAT_01a238a0;
      lVar8 = (ulong)(((uint)((int)uVar12 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar12 >> 0xd) * 0x40;
      lVar10 = (ulong)((uVar4 >> 0x12 | 0x3ff) & uVar4) * 0x40;
      lVar11 = *(long *)(lVar6 + 0x10 + lVar10);
      uVar7 = (ulong)((*(uint *)(param_1 + 0x90) & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar10));
      local_2b8 = (lVar11 + uVar7) -
                  ((long)*(int *)(lVar6 + 0x34 + lVar10) & *(ulong *)(lVar11 + 8 + uVar7));
      lVar11 = *(long *)(lVar6 + 0x10 + lVar8);
      uVar7 = (ulong)((uVar12 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
      local_2b0 = ((lVar11 + uVar7) -
                  ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar11 + 8 + uVar7))) +
                  *(long *)(param_1 + 0xa0);
      local_298 = *(undefined4 *)(param_1 + 0xa8);
      local_2a8 = *(undefined8 *)(param_1 + 0x98);
      local_2a0 = *(undefined8 *)(param_1 + 0xa0);
      FUN_00bdcfa0(&local_2b8,param_2,param_3);
      FUN_006ed9f0(uVar13);
    }
    if (*(int *)(param_1 + 0x150) != -1) {
      lVar6 = FUN_00764290();
      bVar14 = true;
      if (lVar6 != 0) {
        bVar14 = *(char *)(lVar6 + 0x5764) != '\0';
      }
      uVar5 = FUN_00913fa0(*(undefined4 *)(param_1 + 0x2c));
      uVar5 = FUN_00919ee0(uVar5,bVar14,&local_2bc);
      cVar2 = FUN_005c4590();
      uVar9 = 1;
      if ((cVar2 != '\0') && (uVar9 = 1, *(char *)(param_3 + 0xb) != '\x01')) {
        uVar9 = 2;
      }
      local_148 = 0x811c9dc5;
      local_128 = 0x811c9dc5;
      local_108 = 0x811c9dc5;
      local_e8 = 0x811c9dc5;
      local_c8 = 0x811c9dc5;
      local_a8 = 0x811c9dc5;
      local_88 = 0x811c9dc5;
      local_68 = 0x811c9dc5;
      local_60 = 0;
      local_5c = 0x811c9dc5;
      local_58 = 0x811c9dc5;
      local_54 = 0x811c9dc5;
      local_50 = 0x811c9dc5;
      local_4c = 0x811c9dc5;
      local_48 = 0x811c9dc5;
      local_44 = 0x811c9dc5;
      local_40 = 0x811c9dc5;
      FUN_0066b220(param_3 + 0x180,*(undefined1 *)(param_3 + 9),*(undefined1 *)(param_3 + 8),uVar9,
                   uVar5,local_2bc,local_160);
      uVar12 = (int)*(uint *)(param_1 + 0x150) >> 0xd;
      lVar8 = (ulong)((uVar12 >> 0x12 | 0x3ff) & uVar12) * 0x40;
      lVar6 = *DAT_01a238a0;
      lVar11 = *(long *)(lVar6 + 0x10 + lVar8);
      uVar7 = (ulong)((*(uint *)(param_1 + 0x150) & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
      FUN_006422a0((lVar11 + uVar7) -
                   ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar11 + 8 + uVar7)),local_160
                  );
    }
    FUN_00511dc0(uVar13,param_3 + 0xc);
    local_168 = 0;
    local_166 = 0;
    local_164 = 0;
    uVar12 = *(uint *)(param_1 + 0x68);
    if (uVar12 != 0xffffffff) {
      local_2c8 = 0;
      uVar4 = (int)*(uint *)(param_1 + 0x60) >> 0xd;
      lVar6 = *DAT_01a238a0;
      lVar8 = (ulong)(((uint)((int)uVar12 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar12 >> 0xd) * 0x40;
      lVar10 = (ulong)((uVar4 >> 0x12 | 0x3ff) & uVar4) * 0x40;
      lVar11 = *(long *)(lVar6 + 0x10 + lVar10);
      uVar7 = (ulong)((*(uint *)(param_1 + 0x60) & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar10));
      local_2f0 = (lVar11 + uVar7) -
                  ((long)*(int *)(lVar6 + 0x34 + lVar10) & *(ulong *)(lVar11 + 8 + uVar7));
      lVar11 = *(long *)(lVar6 + 0x10 + lVar8);
      uVar7 = (ulong)((uVar12 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
      local_2e8 = ((lVar11 + uVar7) -
                  ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar11 + 8 + uVar7))) +
                  *(long *)(param_1 + 0x70);
      local_2d0 = *(undefined4 *)(param_1 + 0x78);
      local_2e0 = *(undefined8 *)(param_1 + 0x68);
      local_2d8 = *(undefined8 *)(param_1 + 0x70);
      FUN_00bf24c0(&local_2f0,param_2,param_3,&local_168);
    }
    if (*(uint *)(param_1 + 0x148) != 0xffffffff) {
      uVar7 = (ulong)((*(uint *)(param_1 + 0x148) & 0x1fff) * DAT_02689800);
      FUN_0068a160((DAT_026897f8 + uVar7) -
                   ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar7)),param_2,param_3);
    }
    uVar12 = *(uint *)(param_1 + 0x68);
    if (uVar12 != 0xffffffff) {
      local_2f8 = 0;
      uVar4 = (int)*(uint *)(param_1 + 0x60) >> 0xd;
      lVar6 = *DAT_01a238a0;
      lVar10 = (ulong)(((uint)((int)uVar12 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar12 >> 0xd) * 0x40;
      lVar8 = (ulong)((uVar4 >> 0x12 | 0x3ff) & uVar4) * 0x40;
      lVar11 = *(long *)(lVar6 + 0x10 + lVar8);
      uVar7 = (ulong)((*(uint *)(param_1 + 0x60) & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
      local_320 = (lVar11 + uVar7) -
                  ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar11 + 8 + uVar7));
      lVar11 = *(long *)(lVar6 + 0x10 + lVar10);
      uVar7 = (ulong)((uVar12 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar10));
      local_318 = ((lVar11 + uVar7) -
                  ((long)*(int *)(lVar6 + 0x34 + lVar10) & *(ulong *)(lVar11 + 8 + uVar7))) +
                  *(long *)(param_1 + 0x70);
      local_300 = *(undefined4 *)(param_1 + 0x78);
      local_310 = *(undefined8 *)(param_1 + 0x68);
      local_308 = *(undefined8 *)(param_1 + 0x70);
      FUN_00354fc0(&local_320,param_3,&local_168);
    }
    FUN_00353e40(&local_288);
    FUN_00355490(&local_288);
    *(undefined4 *)(param_1 + 0x1208) = *(undefined4 *)(param_3 + 0x358);
    puVar1 = PTR_DAT_019b3fd8;
    uVar13 = uVar13 & 0x1fff;
    *(undefined4 *)(param_1 + 0x120c) = *(undefined4 *)(param_3 + 0x360);
    *(undefined4 *)(param_1 + 0x1210) = *(undefined4 *)(param_3 + 0x324);
    *(undefined4 *)(param_1 + 0x1214) = *(undefined4 *)(param_3 + 0x328);
    cVar2 = FUN_00337fe0((ulong)(DAT_02692230 * uVar13) + DAT_02692228,*(undefined4 *)puVar1,
                         local_198,0);
    if (cVar2 != '\0') {
      lVar8 = (ulong)(((uint)((int)local_180 >> 0xd) >> 0x12 | 0x3ff) & (int)local_180 >> 0xd) *
              0x40;
      lVar6 = *DAT_01a238a0;
      lVar11 = *(long *)(lVar6 + 0x10 + lVar8);
      uVar7 = (ulong)((local_180 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
      uVar12 = *(uint *)(local_178 + 0x24 +
                        ((lVar11 + uVar7) -
                        ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar11 + 8 + uVar7))));
      if (uVar12 != 0xffffffff) {
        lVar8 = (ulong)(((uint)((int)uVar12 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar12 >> 0xd) * 0x40;
        lVar6 = *DAT_01a238a0;
        lVar11 = *(long *)(lVar6 + 0x10 + lVar8);
        uVar7 = (ulong)((uVar12 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
        if (lVar11 + uVar7 !=
            ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar11 + 8 + uVar7))) {
          FUN_006be9d0();
        }
      }
    }
    cVar2 = FUN_00337fe0((ulong)(DAT_02692230 * uVar13) + DAT_02692228,
                         *(undefined4 *)PTR_DAT_019b2928,local_1c8,0);
    if (cVar2 != '\0') {
      lVar8 = (ulong)(((uint)((int)local_1b0 >> 0xd) >> 0x12 | 0x3ff) & (int)local_1b0 >> 0xd) *
              0x40;
      lVar6 = *DAT_01a238a0;
      lVar11 = *(long *)(lVar6 + 0x10 + lVar8);
      uVar7 = (ulong)((local_1b0 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
      uVar12 = *(uint *)(local_1a8 + 0x24 +
                        ((lVar11 + uVar7) -
                        ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar11 + 8 + uVar7))));
      if (uVar12 != 0xffffffff) {
        lVar8 = (ulong)(((uint)((int)uVar12 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar12 >> 0xd) * 0x40;
        lVar6 = *DAT_01a238a0;
        lVar11 = *(long *)(lVar6 + 0x10 + lVar8);
        uVar7 = (ulong)((uVar12 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
        lVar6 = (lVar11 + uVar7) -
                ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar11 + 8 + uVar7));
        if (lVar6 != 0) {
          FUN_003aa420(lVar6,param_2,param_3);
        }
      }
    }
    cVar2 = FUN_00337fe0((ulong)(DAT_02692230 * uVar13) + DAT_02692228,
                         *(undefined4 *)PTR_DAT_019b1a58,local_228,0);
    if (cVar2 != '\0') {
      lVar8 = (ulong)(((uint)((int)local_210 >> 0xd) >> 0x12 | 0x3ff) & (int)local_210 >> 0xd) *
              0x40;
      lVar6 = *DAT_01a238a0;
      lVar11 = *(long *)(lVar6 + 0x10 + lVar8);
      uVar7 = (ulong)((local_210 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
      uVar12 = *(uint *)(local_208 + 0x24 +
                        ((lVar11 + uVar7) -
                        ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar11 + 8 + uVar7))));
      if (uVar12 != 0xffffffff) {
        lVar8 = (ulong)(((uint)((int)uVar12 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar12 >> 0xd) * 0x40;
        lVar6 = *DAT_01a238a0;
        lVar11 = *(long *)(lVar6 + 0x10 + lVar8);
        uVar7 = (ulong)((uVar12 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
        if (lVar11 + uVar7 !=
            ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar11 + 8 + uVar7))) {
          FUN_004bab90();
        }
      }
    }
    cVar2 = FUN_00337fe0((ulong)(uVar13 * DAT_02692230) + DAT_02692228,
                         *(undefined4 *)PTR_DAT_019b29b8,local_258,0);
    if (cVar2 != '\0') {
      lVar8 = (ulong)(((uint)((int)local_240 >> 0xd) >> 0x12 | 0x3ff) & (int)local_240 >> 0xd) *
              0x40;
      lVar6 = *DAT_01a238a0;
      lVar11 = *(long *)(lVar6 + 0x10 + lVar8);
      uVar7 = (ulong)((local_240 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
      uVar12 = *(uint *)(local_238 + 0x24 +
                        ((lVar11 + uVar7) -
                        ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar11 + 8 + uVar7))));
      if (uVar12 != 0xffffffff) {
        lVar8 = (ulong)(((uint)((int)uVar12 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar12 >> 0xd) * 0x40;
        lVar6 = *DAT_01a238a0;
        lVar11 = *(long *)(lVar6 + 0x10 + lVar8);
        uVar7 = (ulong)((uVar12 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar8));
        lVar6 = (lVar11 + uVar7) -
                ((long)*(int *)(lVar6 + 0x34 + lVar8) & *(ulong *)(lVar11 + 8 + uVar7));
        if (lVar6 != 0) {
          *(undefined1 *)(lVar6 + 0x286) = *(undefined1 *)(param_3 + 9);
        }
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

