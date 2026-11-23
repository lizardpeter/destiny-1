
void FUN_007afb70(long param_1,long param_2)

{
  undefined4 uVar1;
  undefined4 uVar2;
  uint uVar3;
  char cVar4;
  undefined1 uVar5;
  undefined4 uVar6;
  int iVar7;
  long lVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  long lVar11;
  undefined4 local_1a8 [2];
  undefined4 local_1a0 [2];
  undefined4 local_198 [2];
  undefined4 local_190;
  undefined4 local_18c;
  undefined4 local_188 [2];
  uint local_180 [2];
  undefined8 local_178;
  undefined4 local_16c;
  undefined8 local_168;
  undefined4 local_15c;
  undefined1 local_158 [288];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (param_2 != 0) {
    local_15c = 0xffffffff;
    local_168 = 0;
    local_16c = 0xffffffff;
    local_178 = 0;
    local_180[0] = 0xffffffff;
    FUN_007b1f80(&local_15c,&local_168,&local_16c,&local_178,local_180);
    uVar6 = FUN_002a2d90(param_2);
    *(undefined4 *)(param_1 + 0xc) = uVar6;
    lVar8 = FUN_002a2980(param_2);
    *(undefined2 *)(param_1 + 0x10) = *(undefined2 *)(lVar8 + 0x680);
    cVar4 = FUN_0025cc10();
    if (cVar4 != '\0') {
      FUN_002642d0(local_188,*(undefined2 *)(param_1 + 0x10));
      *(undefined4 *)(param_1 + 0xb740) = local_188[0];
    }
    FUN_0066cb80(param_1 + 0xb744);
    FUN_0066df40(param_1 + 0xb73c);
    uVar9 = FUN_000596c0();
    FUN_00065030(param_1 + 0x12,uVar9,0x200);
    uVar5 = FUN_0003b180();
    *(undefined1 *)(param_1 + 0x212) = uVar5;
    if (local_180[0] != 0xffffffff) {
      local_18c = 0xffffffff;
      local_190 = 0xffffffff;
      local_198[0] = 0xffffffff;
      local_1a0[0] = 0xffffffff;
      local_1a8[0] = 0xffffffff;
      lVar11 = (ulong)((local_180[0] & 0x1fff) * DAT_02692230) + DAT_02692228;
      FUN_0066bc30(lVar11,&local_18c,&local_190,local_198,local_1a0,local_1a8);
      FUN_0066bdd0(lVar11,local_158);
      FUN_007b2060(param_1 + 0x218);
      FUN_007b2170(param_1 + 0x268);
      lVar8 = FUN_0034e610();
      if (*(char *)(lVar8 + 3) != '\0') {
        FUN_0066dfb0(param_1 + 0x540);
      }
      lVar8 = FUN_0034e610();
      if (*(char *)(lVar8 + 0x18) != '\0') {
        if (DAT_0295b330 == '\0') {
          iVar7 = thunk_FUN_012aa7d6(&DAT_0295b330);
          if (iVar7 != 0) {
            DAT_0295b320 = &PTR_FUN_01949660;
            DAT_0295b328 = 0;
            thunk_FUN_012aa7e6(&DAT_0295b330);
          }
        }
        uVar6 = FUN_008b64d0(&DAT_0295b320);
        *(undefined4 *)(param_1 + 0x53c) = uVar6;
      }
      uVar9 = local_168;
      lVar8 = FUN_0034e610();
      if (*(char *)(lVar8 + 7) != '\0') {
        FUN_0066e100(uVar9,param_1 + 0x580);
      }
      uVar1 = local_15c;
      uVar10 = local_178;
      uVar3 = local_180[0];
      uVar6 = local_18c;
      lVar8 = FUN_0034e610();
      if (*(char *)(lVar8 + 8) != '\0') {
        *(undefined4 *)(param_1 + 0x5b8) = uVar6;
        FUN_0066e850(uVar1,uVar10,uVar3,param_1 + 0x5b0);
      }
      lVar8 = FUN_0034e610();
      if (*(char *)(lVar8 + 9) != '\0') {
        FUN_0066ea10(uVar1,param_1 + 0x5cc);
      }
      lVar8 = FUN_0034e610();
      if (*(char *)(lVar8 + 10) != '\0') {
        FUN_0066e140(uVar9,lVar11,local_158,param_1 + 0x5dc);
      }
      uVar2 = local_190;
      uVar1 = local_198[0];
      uVar6 = local_1a0[0];
      lVar8 = FUN_0034e610();
      if (*(char *)(lVar8 + 0xb) != '\0') {
        FUN_0066e740(uVar2,uVar1,uVar6,param_1 + 0x624);
      }
      FUN_0066eaa0(local_18c,local_190,local_198[0],local_1a0[0],param_1 + 0x5c4);
      FUN_0066e3e0(param_1 + 0x5d4);
      uVar10 = FUN_00059330();
      *(undefined8 *)(param_1 + 0x968) = uVar10;
      FUN_007b22c0(uVar9,param_1 + 0x970);
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

