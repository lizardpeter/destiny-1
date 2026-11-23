
void FUN_0063d290(undefined1 *param_1,undefined4 param_2,undefined8 param_3,long param_4)

{
  uint uVar1;
  undefined8 uVar2;
  long lVar3;
  undefined8 uVar4;
  char cVar5;
  uint uVar6;
  int *piVar7;
  ulong uVar8;
  undefined8 *puVar9;
  long lVar10;
  long lVar11;
  long lVar12;
  int iVar13;
  undefined4 uVar14;
  long local_68;
  long local_60;
  undefined8 local_58;
  undefined8 local_50;
  undefined4 local_48;
  undefined1 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  *param_1 = (char)param_2;
  switch(param_2) {
  case 2:
    puVar9 = (undefined8 *)FUN_0023dfa0(param_1 + 0xac);
    uVar2 = *puVar9;
    uVar1 = *(uint *)(param_1 + 0xd0);
    iVar13 = 3;
    if (uVar1 != 0xffffffff) {
      local_40 = 0;
      uVar6 = (int)*(uint *)(param_1 + 200) >> 0xd;
      lVar12 = *DAT_01a238a0;
      lVar10 = (ulong)(((uint)((int)uVar1 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar1 >> 0xd) * 0x40;
      lVar11 = (ulong)((uVar6 >> 0x12 | 0x3ff) & uVar6) * 0x40;
      lVar3 = *(long *)(lVar12 + 0x10 + lVar11);
      uVar8 = (ulong)((*(uint *)(param_1 + 200) & 0x1fff) * *(int *)(lVar12 + 0x30 + lVar11));
      local_68 = (lVar3 + uVar8) -
                 ((long)*(int *)(lVar12 + 0x34 + lVar11) & *(ulong *)(lVar3 + 8 + uVar8));
      lVar3 = *(long *)(lVar12 + 0x10 + lVar10);
      uVar8 = (ulong)((uVar1 & 0x1fff) * *(int *)(lVar12 + 0x30 + lVar10));
      local_60 = ((lVar3 + uVar8) -
                 ((long)*(int *)(lVar12 + 0x34 + lVar10) & *(ulong *)(lVar3 + 8 + uVar8))) +
                 *(long *)(param_1 + 0xd8);
      local_48 = *(undefined4 *)(param_1 + 0xe0);
      local_58 = *(undefined8 *)(param_1 + 0xd0);
      local_50 = *(undefined8 *)(param_1 + 0xd8);
      cVar5 = FUN_00353610(&local_68);
      iVar13 = (int)cVar5;
    }
    iVar13 = FUN_0063bb10(uVar2,iVar13,0,param_4,1);
    *(int *)(param_1 + 0xb0) = iVar13;
    *(undefined4 *)(param_1 + 0x68) = *(undefined4 *)(param_4 + 0xec);
    *(undefined8 *)(param_1 + 0x60) = *(undefined8 *)(param_4 + 0xe4);
    *(undefined8 *)(param_1 + 0x58) = *(undefined8 *)(param_4 + 0xdc);
    uVar4 = *(undefined8 *)(param_4 + 0xcc);
    *(undefined8 *)(param_1 + 0x50) = *(undefined8 *)(param_4 + 0xd4);
    *(undefined8 *)(param_1 + 0x48) = uVar4;
    *(undefined4 *)(param_1 + 0x6c) = *(undefined4 *)(param_4 + 0xf0);
    *(undefined4 *)(param_1 + 0x70) = *(undefined4 *)(param_4 + 0xf4);
    *(undefined4 *)(param_1 + 0x74) = *(undefined4 *)(param_4 + 0xf8);
    *(undefined4 *)(param_1 + 0x78) = *(undefined4 *)(param_4 + 0xfc);
    *(undefined4 *)(param_1 + 0x7c) = *(undefined4 *)(param_4 + 0x100);
    *(undefined4 *)(param_1 + 0x80) = *(undefined4 *)(param_4 + 0x104);
    *(undefined4 *)(param_1 + 0x84) = *(undefined4 *)(param_4 + 0x108);
    *(undefined4 *)(param_1 + 0x88) = *(undefined4 *)(param_4 + 0x10c);
    *(undefined4 *)(param_1 + 0x8c) = *(undefined4 *)(param_4 + 0x110);
    *(undefined4 *)(param_1 + 0x90) = *(undefined4 *)(param_4 + 0x114);
    *(undefined4 *)(param_1 + 0x94) = *(undefined4 *)(param_4 + 0x118);
    *(undefined4 *)(param_1 + 0x98) = *(undefined4 *)(param_4 + 0x11c);
    *(undefined4 *)(param_1 + 0x9c) = *(undefined4 *)(param_4 + 0x120);
    *(undefined4 *)(param_1 + 0xa0) = *(undefined4 *)(param_4 + 0x124);
    *(undefined4 *)(param_1 + 0xa4) = *(undefined4 *)(param_4 + 0x128);
    *(undefined4 *)(param_1 + 0xa8) = *(undefined4 *)(param_4 + 300);
    if ((iVar13 != -1) && (piVar7 = (int *)FUN_0063bef0(uVar2,iVar13), *piVar7 == 6)) {
      FUN_0063d290(param_1,3,param_3,param_4);
    }
    break;
  case 3:
    if (param_1[0xf0] == '\0') {
      FUN_0063cd80(param_1);
      lVar12 = 0;
      do {
        uVar14 = 0xffffffff;
        if (*(uint *)(param_1 + 4) != 0xffffffff) {
          uVar8 = (ulong)((*(uint *)(param_1 + 4) & 0x1fff) * DAT_02689800);
          uVar14 = *(undefined4 *)
                    (((DAT_026897f8 + uVar8) -
                     ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar8))) + 0x2c);
        }
        FUN_0063e9d0(param_1 + lVar12 + 8,uVar14);
        lVar12 = lVar12 + 8;
      } while ((int)lVar12 != 0x40);
    }
    else {
      FUN_0063dca0();
    }
    if (*(int *)(param_1 + 0xb4) != -1) {
      puVar9 = (undefined8 *)FUN_0023dfa0(param_1 + 0xac);
      FUN_0063be90(*puVar9,*(undefined4 *)(param_1 + 0xb4),1);
    }
    *(undefined4 *)(param_1 + 0xb4) = *(undefined4 *)(param_1 + 0xb0);
    *(undefined4 *)(param_1 + 0xb0) = 0xffffffff;
    if (*(int *)(param_1 + 0xd0) != -1) {
      FUN_0063de20(param_1,param_1 + 0x48);
      FUN_0063e030(param_1);
      FUN_0063e1c0(param_1);
      FUN_0063e460(param_1);
      FUN_0063e530(param_1);
    }
    FUN_0063e6c0(param_1);
    uVar14 = 0xffffffff;
    if (*(uint *)(param_1 + 4) != 0xffffffff) {
      uVar8 = (ulong)((*(uint *)(param_1 + 4) & 0x1fff) * DAT_02689800);
      uVar14 = *(undefined4 *)
                (((DAT_026897f8 + uVar8) -
                 ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar8))) + 0x2c);
    }
    FUN_002fc580(uVar14);
    break;
  case 4:
    if (param_1[0xf0] == '\0') {
      FUN_0063cd80(param_1);
      lVar12 = 8;
      do {
        uVar14 = 0xffffffff;
        if (*(uint *)(param_1 + 4) != 0xffffffff) {
          uVar8 = (ulong)((*(uint *)(param_1 + 4) & 0x1fff) * DAT_02689800);
          uVar14 = *(undefined4 *)
                    (((DAT_026897f8 + uVar8) -
                     ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar8))) + 0x2c);
        }
        FUN_0063e9d0(param_1 + lVar12,uVar14);
        lVar12 = lVar12 + 8;
      } while ((int)lVar12 != 0x48);
      FUN_0063d7f0(param_1,param_3);
    }
    if (*(int *)(param_1 + 0xb4) != -1) {
      puVar9 = (undefined8 *)FUN_0023dfa0(param_1 + 0xac);
      FUN_0063be90(*puVar9,*(undefined4 *)(param_1 + 0xb4),1);
      *(undefined4 *)(param_1 + 0xb4) = 0xffffffff;
    }
    if (*(int *)(param_1 + 0xb0) != -1) {
      puVar9 = (undefined8 *)FUN_0023dfa0(param_1 + 0xac);
      FUN_0063be90(*puVar9,*(undefined4 *)(param_1 + 0xb0),1);
      *(undefined4 *)(param_1 + 0xb0) = 0xffffffff;
    }
    FUN_0063e6c0(param_1);
    uVar14 = 0xffffffff;
    if (*(uint *)(param_1 + 4) != 0xffffffff) {
      uVar8 = (ulong)((*(uint *)(param_1 + 4) & 0x1fff) * DAT_02689800);
      uVar14 = *(undefined4 *)
                (((DAT_026897f8 + uVar8) -
                 ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar8))) + 0x2c);
    }
    FUN_002fc580(uVar14);
    *param_1 = 1;
  case 1:
    if (*(int *)(param_1 + 0xb0) != -1) {
      puVar9 = (undefined8 *)FUN_0023dfa0(param_1 + 0xac);
      FUN_0063be90(*puVar9,*(undefined4 *)(param_1 + 0xb0),1);
      *(undefined4 *)(param_1 + 0xb0) = 0xffffffff;
    }
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

