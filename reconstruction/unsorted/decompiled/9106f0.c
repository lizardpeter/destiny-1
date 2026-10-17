
void FUN_009106f0(long param_1,long param_2,int *param_3)

{
  char cVar1;
  int iVar2;
  undefined8 uVar3;
  long lVar4;
  undefined4 *puVar5;
  undefined8 uVar6;
  long lVar7;
  ushort uVar8;
  long extraout_RDX;
  uint uVar9;
  bool bVar10;
  undefined1 auVar11 [16];
  undefined4 local_48 [2];
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar7 = *(long *)(PTR_DAT_019b1b98 + 8);
  uVar3 = FUN_000e8680(lVar7,0,0xffffffff);
  thunk_FUN_012aa986(param_3,0,uVar3);
  uVar8 = *(ushort *)(lVar7 + 0x1c) & 0x78;
  bVar10 = uVar8 != 0;
  if (uVar8 == 0) {
    uVar9 = *(uint *)(lVar7 + 0x20);
    if ((*(ushort *)(lVar7 + 0x1c) & 0x40) != 0) {
      if ((param_3 == (int *)0x0) || (lVar4 = FUN_000e8a90(lVar7,param_3), lVar4 == 0)) {
        uVar9 = uVar9 | 0x5488bf;
      }
      else {
        uVar9 = uVar9 | *(uint *)(lVar4 + 0x20) & 0x5488bf;
      }
    }
    bVar10 = (uVar9 & 0xc08070) != 0;
  }
  if (bVar10) {
    FUN_000e6730(lVar7,param_3,0,0xffffffff,0);
  }
  uVar3 = FUN_005494c0();
  FUN_0054b0c0(uVar3);
  puVar5 = (undefined4 *)FUN_0054c7b0(uVar3,*(undefined2 *)(param_1 + 10));
  *param_3 = -1;
  if (puVar5 != (undefined4 *)0x0) {
    uVar6 = FUN_0033fa20();
    local_48[0] = *puVar5;
    iVar2 = FUN_0033fc20(uVar6,local_48);
    if (iVar2 != -1) {
      *param_3 = iVar2;
    }
    param_3[3] = puVar5[3];
  }
  cVar1 = *(char *)(extraout_RDX + 0xd);
  uVar6 = FUN_005494c0();
  iVar2 = -1;
  if (cVar1 != -1) {
    lVar7 = 0;
    do {
      if (*(char *)(param_1 + 0x28 + lVar7 * 4) == cVar1) {
        puVar5 = (undefined4 *)FUN_0054c6b0(uVar6,*(undefined2 *)(param_1 + 0x2a + lVar7 * 4));
        if (puVar5 != (undefined4 *)0x0) {
          uVar6 = FUN_0033fa20();
          local_40[0] = *puVar5;
          iVar2 = FUN_0033fc20(uVar6,local_40);
        }
        break;
      }
      lVar7 = lVar7 + 1;
    } while ((int)lVar7 < 6);
  }
  param_3[2] = iVar2;
  if (param_2 != 0) {
    uVar6 = FUN_005494c0();
    auVar11 = FUN_0054b1b0(uVar6,*(undefined2 *)(param_2 + 8));
    lVar4 = auVar11._8_8_;
    lVar7 = auVar11._0_8_;
    if ((((lVar4 != 0) && (lVar7 != 0)) && (*(long *)(lVar7 + 0x18) != 0)) &&
       (((*(long *)(lVar4 + 0x18) != 0 && (lVar7 + 0x18 + *(long *)(lVar7 + 0x18) != 0)) &&
        ((*(long *)(lVar4 + 0x18) != -(lVar4 + 0x18) &&
         (lVar7 = FUN_00549df0(uVar3,*(undefined2 *)(*(long *)(lVar4 + 0x18) + 0x1a + lVar4)),
         lVar7 != 0)))))) {
      param_3[1] = *(int *)(lVar7 + 4);
    }
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

