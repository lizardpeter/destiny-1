
void FUN_009101f0(long param_1,undefined8 param_2,int *param_3)

{
  char cVar1;
  int iVar2;
  undefined8 uVar3;
  long lVar4;
  undefined4 *puVar5;
  long lVar6;
  ushort uVar7;
  long extraout_RDX;
  uint uVar8;
  bool bVar9;
  undefined4 local_40 [2];
  undefined4 local_38 [2];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  lVar6 = *(long *)(PTR_DAT_019b1b88 + 8);
  uVar3 = FUN_000e8680(lVar6,0,0xffffffff);
  thunk_FUN_012aa986(param_3,0,uVar3);
  uVar7 = *(ushort *)(lVar6 + 0x1c) & 0x78;
  bVar9 = uVar7 != 0;
  if (uVar7 == 0) {
    uVar8 = *(uint *)(lVar6 + 0x20);
    if ((*(ushort *)(lVar6 + 0x1c) & 0x40) != 0) {
      if ((param_3 == (int *)0x0) || (lVar4 = FUN_000e8a90(lVar6,param_3), lVar4 == 0)) {
        uVar8 = uVar8 | 0x5488bf;
      }
      else {
        uVar8 = uVar8 | *(uint *)(lVar4 + 0x20) & 0x5488bf;
      }
    }
    bVar9 = (uVar8 & 0xc08070) != 0;
  }
  if (bVar9) {
    FUN_000e6730(lVar6,param_3,0,0xffffffff,0);
  }
  uVar3 = FUN_005494c0();
  FUN_0054b0c0(uVar3);
  puVar5 = (undefined4 *)FUN_0054c7b0(uVar3,*(undefined2 *)(param_1 + 10));
  *param_3 = -1;
  if (puVar5 != (undefined4 *)0x0) {
    uVar3 = FUN_0033fa20();
    local_40[0] = *puVar5;
    iVar2 = FUN_0033fc20(uVar3,local_40);
    if (iVar2 != -1) {
      *param_3 = iVar2;
    }
    param_3[2] = puVar5[3];
  }
  cVar1 = *(char *)(extraout_RDX + 0xc);
  uVar3 = FUN_005494c0();
  iVar2 = -1;
  if (cVar1 != -1) {
    lVar6 = 0;
    do {
      if (*(char *)(param_1 + 0x28 + lVar6 * 4) == cVar1) {
        puVar5 = (undefined4 *)FUN_0054c6b0(uVar3,*(undefined2 *)(param_1 + 0x2a + lVar6 * 4));
        if (puVar5 != (undefined4 *)0x0) {
          uVar3 = FUN_0033fa20();
          local_38[0] = *puVar5;
          iVar2 = FUN_0033fc20(uVar3,local_38);
        }
        break;
      }
      lVar6 = lVar6 + 1;
    } while ((int)lVar6 < 6);
  }
  param_3[1] = iVar2;
  if (*DAT_01a1f100 != local_30) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

