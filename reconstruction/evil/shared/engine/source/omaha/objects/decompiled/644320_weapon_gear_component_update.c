
undefined8 FUN_00644320(uint *param_1)

{
  uint uVar1;
  uint uVar2;
  int iVar3;
  long lVar4;
  ulong uVar5;
  long lVar6;
  undefined8 uVar7;
  uint uVar8;
  long lVar9;
  long lVar10;
  ulong uVar11;
  undefined4 local_1b0;
  undefined4 local_1ac;
  undefined4 local_1a8;
  undefined4 local_1a4;
  undefined4 local_1a0;
  undefined4 local_19c;
  undefined4 local_190;
  undefined4 local_18c;
  undefined4 local_188;
  undefined4 local_184;
  undefined4 local_180;
  undefined4 local_17c;
  undefined4 local_178;
  uint local_174 [51];
  uint local_a8;
  uint local_a4;
  uint local_a0;
  undefined4 local_9c;
  undefined4 local_98;
  undefined4 local_94;
  undefined4 local_90;
  undefined4 local_8c;
  undefined4 local_88;
  undefined4 local_84;
  undefined4 local_80;
  undefined4 local_7c;
  int local_78 [6];
  undefined4 local_60;
  undefined4 local_58;
  undefined4 local_50;
  undefined4 local_48;
  undefined4 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_9c = 0;
  local_98 = 0x811c9dc5;
  local_94 = 0x811c9dc5;
  local_90 = 0x811c9dc5;
  local_8c = 0x811c9dc5;
  local_88 = 0x811c9dc5;
  local_84 = 0x811c9dc5;
  local_80 = 0x811c9dc5;
  local_7c = 0x811c9dc5;
  local_78[0] = -0x7ee3623b;
  local_78[2] = 0x811c9dc5;
  local_78[4] = 0x811c9dc5;
  local_60 = 0x811c9dc5;
  local_58 = 0x811c9dc5;
  local_50 = 0x811c9dc5;
  local_48 = 0x811c9dc5;
  local_40 = 0x811c9dc5;
  uVar8 = param_1[0x67];
  FUN_0063c9c0(local_174 + 3);
  if ((char)uVar8 != '\0') {
    uVar8 = param_1[0x23];
    uVar1 = param_1[0x21];
    uVar2 = param_1[0x22];
    lVar9 = 0;
    lVar10 = 6;
    do {
      *(undefined4 *)((long)local_174 + lVar10 * 2) = *(undefined4 *)((long)param_1 + lVar9 + 0x68);
      *(uint *)((long)local_174 + lVar10 * 2 + 4) = uVar1;
      *(uint *)((long)local_174 + lVar10 * 2 + 8) = uVar2;
      *(uint *)((long)local_174 + lVar10 * 2 + 0xc) = uVar8;
      iVar3 = *(int *)((long)param_1 + lVar9 * 2 + 0x30);
      if (iVar3 != -0x7ee3623b) {
        *(int *)((long)local_78 + lVar9 * 2) = iVar3;
        *(undefined4 *)((long)local_78 + lVar9 * 2 + 4) =
             *(undefined4 *)((long)param_1 + lVar9 * 2 + 0x34);
      }
      lVar10 = lVar10 + 0xc;
      lVar9 = lVar9 + 4;
    } while ((int)lVar9 != 0x1c);
    local_a0 = param_1[0x24];
    local_a8 = param_1[0x25];
    local_a4 = param_1[0x26];
  }
  uVar8 = (int)*param_1 >> 0xd;
  lVar9 = *(long *)(param_1 + 2);
  lVar10 = *DAT_01a238a0;
  lVar6 = (ulong)((uVar8 >> 0x12 | 0x3ff) & uVar8) * 0x40;
  lVar4 = *(long *)(lVar10 + 0x10 + lVar6);
  iVar3 = *(int *)(lVar10 + 0x34 + lVar6);
  uVar11 = (ulong)((*param_1 & 0x1fff) * *(int *)(lVar10 + 0x30 + lVar6));
  uVar5 = *(ulong *)(lVar4 + 8 + uVar11);
  local_190 = 0;
  local_18c = 0x811c9dc5;
  local_188 = 0x811c9dc5;
  local_184 = 0x811c9dc5;
  local_180 = 0x811c9dc5;
  local_17c = 0x811c9dc5;
  local_178 = 0x811c9dc5;
  local_174[0] = 0x811c9dc5;
  local_174[1] = 0x811c9dc5;
  FUN_0063c990(&local_1b0);
  lVar10 = (lVar4 + uVar11) - ((long)iVar3 & uVar5);
  local_1b0 = *(undefined4 *)(lVar9 + 0xa8 + lVar10);
  local_1ac = *(undefined4 *)(lVar9 + 0xb8 + lVar10);
  local_1a8 = *(undefined4 *)(lVar9 + 200 + lVar10);
  local_1a4 = *(undefined4 *)(lVar9 + 0xd8 + lVar10);
  local_1a0 = *(undefined4 *)(lVar9 + 0xe8 + lVar10);
  local_19c = *(undefined4 *)(lVar9 + 0xf8 + lVar10);
  if (*(char *)((long)param_1 + 0x19d) == '\0') {
    *(undefined1 *)((long)param_1 + 0x19d) = 1;
    FUN_0063d0e0(param_1 + 0x28,&local_1b0,local_174 + 3);
    uVar7 = 1;
  }
  else {
    uVar7 = FUN_0063dbb0(param_1 + 0x28,&local_1b0,local_174 + 3);
  }
  if (*DAT_01a1f100 == local_38) {
    return uVar7;
  }
  uVar7 = thunk_FUN_012aa7f6();
  return uVar7;
}

