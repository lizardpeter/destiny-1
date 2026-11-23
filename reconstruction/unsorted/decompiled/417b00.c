
void FUN_00417b00(long param_1)

{
  undefined4 uVar1;
  short sVar2;
  undefined4 *puVar3;
  long lVar4;
  undefined *puVar5;
  char cVar6;
  uint uVar7;
  long lVar8;
  long lVar9;
  ulong uVar10;
  long lVar11;
  long extraout_RDX;
  int iVar12;
  code *pcVar13;
  undefined8 local_98;
  ulong local_90;
  undefined8 local_88;
  undefined4 local_80;
  undefined4 uStack_7c;
  undefined4 local_78;
  undefined4 uStack_74;
  undefined8 local_70;
  undefined4 local_68;
  undefined4 uStack_64;
  undefined8 local_60;
  undefined8 local_58;
  undefined4 local_50;
  undefined4 uStack_4c;
  undefined8 local_48;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar8 = FUN_009067e0();
  lVar9 = FUN_003dd380();
  puVar3 = *(undefined4 **)(param_1 + 8);
  *puVar3 = 0;
  if (*(short *)(lVar8 + 0x188e) != -1) {
    cVar6 = FUN_00545230();
    if (cVar6 != '\0') {
      local_40 = 0;
      _local_50 = CONCAT44(*(undefined4 *)PTR_DAT_01996058,DAT_025d7318);
      local_48 = 1;
      FUN_001183d0(puVar3,&local_50);
      local_58 = 0;
      _local_68 = CONCAT44(*(undefined4 *)PTR_DAT_01996020,DAT_025d7314);
      local_60 = 1;
      FUN_001183d0(puVar3,&local_68);
    }
  }
  FUN_001184d0(lVar9 + 0x128,puVar3);
  puVar5 = PTR_DAT_01996068;
  local_78 = *(undefined4 *)(lVar9 + 0x1c);
  uVar1 = *(undefined4 *)(lVar9 + 0x20);
  local_70 = 0;
  _local_80 = CONCAT44(*(undefined4 *)PTR_DAT_01996068,DAT_025d7214);
  uStack_74 = 0;
  FUN_001183d0(puVar3,&local_80);
  _local_80 = CONCAT44(*(undefined4 *)puVar5,DAT_025d7284);
  _local_78 = CONCAT44(uStack_74,uVar1);
  FUN_001183d0(puVar3,&local_80);
  if (0 < *(int *)(&DAT_000012fc + lVar8)) {
    pcVar13 = FUN_00001300 + lVar8;
    iVar12 = 0;
    do {
      FUN_001183d0(puVar3,pcVar13);
      pcVar13 = pcVar13 + 0x18;
      iVar12 = iVar12 + 1;
    } while (iVar12 < *(int *)(&DAT_000012fc + lVar8));
  }
  cVar6 = FUN_00545230(*(undefined2 *)(lVar8 + 0x188e));
  if (cVar6 != '\0') {
    FUN_00272e80((long)*(int *)(lVar8 + 0x1894),lVar8 + 0x1898,puVar3);
  }
  uVar7 = FUN_0010c3d0();
  if (uVar7 != 0xffffffff) {
    lVar11 = (ulong)(((uint)((int)uVar7 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar7 >> 0xd) * 0x40;
    lVar9 = *DAT_01a238a0;
    lVar4 = *(long *)(lVar9 + 0x10 + lVar11);
    uVar10 = (ulong)((uVar7 & 0x1fff) * *(int *)(lVar9 + 0x30 + lVar11));
    lVar9 = (lVar4 + uVar10) -
            ((long)*(int *)(lVar9 + 0x34 + lVar11) & *(ulong *)(lVar4 + 8 + uVar10));
    FUN_00417eb0(extraout_RDX + 0x694 + lVar9,extraout_RDX + 0x1bc + lVar9,puVar3);
  }
  puVar5 = PTR_DAT_01996020;
  lVar9 = FUN_0034e410();
  sVar2 = *(short *)(lVar8 + 0x188e);
  lVar8 = 0;
  do {
    if ((int)sVar2 == *(int *)(lVar9 + 0xc + lVar8 * 4)) {
      local_98 = 0xffffffff811c9dc5;
      local_88 = 0;
      local_90 = 0;
      if (*(char *)(lVar9 + 0x2c + lVar8) != '\0') {
        local_98 = CONCAT44(*(undefined4 *)puVar5,DAT_025d7300);
        local_90 = (ulong)*(byte *)(lVar9 + 0x34 + lVar8);
        FUN_001183d0(puVar3,&local_98);
      }
      if (*(char *)(lVar9 + 0x3c + lVar8) != '\0') {
        local_98 = CONCAT44(*(undefined4 *)puVar5,DAT_025d7304);
        local_90 = CONCAT71(local_90._1_7_,*(undefined1 *)(lVar9 + 0x44 + lVar8));
        FUN_001183d0(puVar3,&local_98);
      }
      if (*(char *)(lVar9 + 0x4c + lVar8) != '\0') {
        local_98 = CONCAT44(*(undefined4 *)puVar5,DAT_025d7308);
        local_90 = CONCAT71(local_90._1_7_,*(undefined1 *)(lVar9 + 0x54 + lVar8));
        FUN_001183d0(puVar3,&local_98);
      }
    }
    lVar8 = lVar8 + 1;
  } while ((int)lVar8 != 8);
  FUN_001185f0(puVar3);
  thunk_FUN_00100de0();
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

