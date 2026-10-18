
void FUN_007dfd10(long param_1,long param_2)

{
  undefined8 *puVar1;
  undefined4 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  char cVar5;
  uint uVar6;
  int iVar7;
  ulong uVar8;
  long lVar9;
  uint local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (*(long *)(param_1 + 0x50) == 0) goto LAB_007dff96;
  uVar8 = 0;
  lVar9 = 0x26e4;
  do {
    if (*(int *)(param_2 + 0xc0 + uVar8 * 4) == 1) {
      local_40[0] = FUN_00f82b00();
      uVar6 = local_40[0] & 0xff;
      if (((((0x16 < uVar6) || (uVar6 == 0)) || ((uVar6 | 2) == 0xf)) ||
          ((cVar5 = FUN_00f7d980(local_40,0), cVar5 == '\0' ||
           (cVar5 = FUN_00f7d780(local_40), cVar5 == '\0')))) || ((char)local_40[0] == '\0'))
      goto LAB_007dfe20;
      if (*(long *)(param_1 + 0x50) != 0) {
        uVar2 = *(undefined4 *)(param_2 + uVar8 * 4);
        FUN_00f8f0e0(*(long *)(param_1 + 0x50),uVar8 & 0xffffffff,param_2 + -0x26d4 + lVar9);
        uVar3 = *(undefined8 *)(param_2 + -0x26b4 + lVar9);
        *(undefined4 *)(param_1 + 0x28 + lVar9) = *(undefined4 *)(param_2 + -0x26ac + lVar9);
        *(undefined8 *)(param_1 + 0x20 + lVar9) = uVar3;
        *(undefined8 *)(param_1 + 0x18 + lVar9) = *(undefined8 *)(param_2 + -0x26bc + lVar9);
        *(undefined8 *)(param_1 + 0x10 + lVar9) = *(undefined8 *)(param_2 + -0x26c4 + lVar9);
        uVar3 = *(undefined8 *)(param_2 + -0x26d4 + lVar9);
        *(undefined8 *)(param_1 + 8 + lVar9) = *(undefined8 *)(param_2 + -0x26cc + lVar9);
        *(undefined8 *)(param_1 + lVar9) = uVar3;
        *(undefined4 *)(&DAT_000027c4 + uVar8 * 4 + param_1) = uVar2;
      }
    }
    else {
LAB_007dfe20:
      if (*(long *)(param_1 + 0x50) != 0) {
        FUN_00f8f0e0(*(long *)(param_1 + 0x50),uVar8 & 0xffffffff,0);
        *(undefined4 *)(param_1 + 0x28 + lVar9) = 0;
        *(undefined8 *)(param_1 + 0x20 + lVar9) = 0;
        *(undefined8 *)(param_1 + 0x18 + lVar9) = 0;
        *(undefined8 *)(param_1 + 0x10 + lVar9) = 0;
        *(undefined8 *)(param_1 + 8 + lVar9) = 0;
        *(undefined8 *)(param_1 + lVar9) = 0;
        *(undefined4 *)(&DAT_000027c4 + uVar8 * 4 + param_1) = 0;
      }
    }
    lVar9 = lVar9 + 0x2c;
    uVar8 = uVar8 + 1;
  } while ((int)uVar8 != 4);
  if (*(int *)(param_2 + 0x108) == 1) {
    puVar1 = (undefined8 *)(param_2 + 0xd4);
    iVar7 = FUN_00f7e440(puVar1);
    if (iVar7 == 0) goto LAB_007dff02;
    if (*(long *)(param_1 + 0x50) != 0) {
      FUN_00f7eec0(*(long *)(param_1 + 0x50),puVar1);
      uVar3 = *(undefined8 *)(param_2 + 0xf4);
      uVar4 = *(undefined8 *)(param_2 + 0xfc);
      *(undefined4 *)(param_1 + 0x26e0) = *(undefined4 *)(param_2 + 0x104);
      *(undefined8 *)(param_1 + 0x26d8) = uVar4;
      *(undefined8 *)(param_1 + 0x26d0) = uVar3;
      *(undefined8 *)(param_1 + 0x26c8) = *(undefined8 *)(param_2 + 0xec);
      *(undefined8 *)(param_1 + 0x26c0) = *(undefined8 *)(param_2 + 0xe4);
      uVar3 = *puVar1;
      *(undefined8 *)(param_1 + 0x26b8) = *(undefined8 *)(param_2 + 0xdc);
      *(undefined8 *)(param_1 + 0x26b0) = uVar3;
    }
  }
  else {
LAB_007dff02:
    if (*(long *)(param_1 + 0x50) != 0) {
      FUN_00f7eec0(*(long *)(param_1 + 0x50),0);
      *(undefined4 *)(param_1 + 0x26e0) = 0;
      *(undefined8 *)(param_1 + 0x26d8) = 0;
      *(undefined8 *)(param_1 + 0x26d0) = 0;
      *(undefined8 *)(param_1 + 0x26c8) = 0;
      *(undefined8 *)(param_1 + 0x26c0) = 0;
      *(undefined8 *)(param_1 + 0x26b8) = 0;
      *(undefined8 *)(param_1 + 0x26b0) = 0;
    }
  }
  if ((*(short *)(param_2 + 0x1b0) != 0) && (*(short *)(param_2 + 0x1b2) != 0)) {
    FUN_007dfac0(0,DAT_0165fe98,param_1,0,0);
  }
LAB_007dff96:
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

