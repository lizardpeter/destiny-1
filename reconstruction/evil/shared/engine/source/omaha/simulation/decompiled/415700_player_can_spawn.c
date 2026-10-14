
ulong FUN_00415700(int param_1)

{
  char cVar1;
  char cVar2;
  ushort uVar3;
  uint uVar4;
  uint uVar5;
  undefined8 uVar6;
  long lVar7;
  undefined *puVar8;
  long lVar9;
  ulong uVar10;
  short sVar11;
  long lVar12;
  char cVar13;
  uint local_174;
  undefined4 local_170 [2];
  undefined1 local_168 [24];
  long local_150;
  short local_148;
  int iStack_144;
  bool local_140;
  undefined1 local_138 [256];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar6 = FUN_003430b0();
  cVar1 = FUN_003455e0(uVar6);
  cVar13 = '\0';
  cVar2 = '\0';
  if (cVar1 != '\0') {
    uVar6 = FUN_003430b0();
    local_170[0] = FUN_00345610(uVar6);
    cVar2 = FUN_0012d730(local_170);
  }
  if (((param_1 == -1) || (lVar7 = FUN_001192b0(param_1), lVar7 == 0)) ||
     (*(char *)(lVar7 + 9) == '\0')) goto LAB_00415a37;
  if (cVar2 == '\0') goto LAB_004157f6;
  cVar1 = FUN_0010c500(&local_174);
  if (cVar1 == '\0') {
    if (local_174 == 0xffffffff) {
      puVar8 = &DAT_01615ab5;
    }
    else {
LAB_004157cf:
      puVar8 = (undefined *)FUN_000e9fa0();
    }
    cVar13 = '\0';
    FUN_010156f0(local_138,s_can_t_spawn_due_to_the_current_a_0162fd86,puVar8);
    goto LAB_00415a37;
  }
  if (local_174 == 0xffffffff) {
    if (local_174 != 0xffffffff) goto LAB_004157f6;
LAB_004157ff:
    uVar4 = FUN_00240840();
    uVar5 = FUN_00240880();
    if (uVar5 != 0xffffffff) {
      lVar12 = (ulong)(((uint)((int)uVar5 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar5 >> 0xd) * 0x40;
      lVar7 = *DAT_01a238a0;
      cVar2 = '\0';
      lVar9 = *(long *)(lVar7 + 0x10 + lVar12);
      uVar10 = (ulong)((uVar5 & 0x1fff) * *(int *)(lVar7 + 0x30 + lVar12));
      if (*(char *)(((lVar9 + uVar10) -
                    ((long)*(int *)(lVar7 + 0x34 + lVar12) & *(ulong *)(lVar9 + 8 + uVar10))) + 0x1c
                   ) == '\0') goto LAB_004158ad;
    }
    cVar2 = '\x01';
    if (uVar4 != 0xffffffff) {
      lVar12 = (ulong)(((uint)((int)uVar4 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar4 >> 0xd) * 0x40;
      lVar7 = *DAT_01a238a0;
      lVar9 = *(long *)(lVar7 + 0x10 + lVar12);
      uVar10 = (ulong)((uVar4 & 0x1fff) * *(int *)(lVar7 + 0x30 + lVar12));
      cVar2 = *(char *)(((lVar9 + uVar10) -
                        ((long)*(int *)(lVar7 + 0x34 + lVar12) & *(ulong *)(lVar9 + 8 + uVar10))) +
                       0x1c) != '\0';
    }
  }
  else {
    if (local_174 < 10) {
      if ((0x3b7U >> (local_174 & 0x1f) & 1) != 0) goto LAB_004157cf;
      if ((0x48U >> (local_174 & 0x1f) & 1) != 0) goto LAB_004157ff;
    }
LAB_004157f6:
    if (cVar2 != '\0') goto LAB_004157ff;
  }
LAB_004158ad:
  if (cVar2 != '\0') {
    local_150 = 0;
    uVar3 = FUN_00107550(0);
    lVar7 = 0;
    local_150 = 0;
    if (uVar3 != 0) {
      local_150 = *(long *)(&DAT_01ad5030 + (ulong)uVar3 * DAT_01ad5010 + DAT_01ad5000);
    }
    local_140 = false;
    uVar3 = FUN_00107550(0);
    if (uVar3 != 0) {
      lVar7 = *(long *)(&DAT_01ad5030 + (ulong)uVar3 * DAT_01ad5010 + DAT_01ad5000);
    }
    iStack_144 = 0xc;
    local_148 = 0;
    local_140 = 0 < *(short *)(lVar7 + 0x2bd4e);
    local_150 = lVar7;
    if (0 < *(short *)(lVar7 + 0x2bd4e)) {
      do {
        cVar1 = FUN_0100d0a0(&local_150,0,local_168);
        if (cVar1 != '\0') {
          lVar7 = FUN_001191e0(param_1);
          lVar9 = FUN_003f3ce0(param_1);
          lVar12 = FUN_003f3de0(param_1);
          if (((lVar9 == 0) || (lVar12 == 0)) ||
             ((cVar13 = '\0', *(char *)(lVar7 + 9) == -1 || (cVar13 = cVar2, cVar2 == '\0'))))
          goto LAB_00415a37;
          goto LAB_00415a28;
        }
        local_148 = local_148 + 1;
        if (local_148 < 0) {
          local_140 = false;
          break;
        }
        if (iStack_144 == -1) {
          sVar11 = *(short *)(local_150 + 0x510);
        }
        else {
          sVar11 = *(short *)(local_150 + 0x2bd1e + (long)iStack_144 * 4);
        }
        local_140 = local_148 < sVar11;
      } while (local_148 < sVar11);
    }
    if (cVar2 != '\0') {
LAB_00415a28:
      cVar1 = FUN_003d5f30();
      cVar13 = '\0';
      if (cVar1 != '\0') goto LAB_00415a37;
    }
  }
  cVar13 = cVar2;
LAB_00415a37:
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),cVar13) & 0xffffffffffffff01;
  }
  uVar10 = thunk_FUN_012aa7f6();
  return uVar10;
}

