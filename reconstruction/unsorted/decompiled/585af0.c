
void FUN_00585af0(ulong *param_1)

{
  ulong *puVar1;
  long lVar2;
  undefined8 uVar3;
  long lVar4;
  ushort uVar5;
  uint uVar6;
  bool bVar7;
  byte local_60 [9];
  uint7 uStack_57;
  ulong local_50;
  ulong local_48;
  ulong local_40;
  ulong local_38;
  long local_30;
  
  local_30 = *DAT_01a1f100;
  lVar2 = *(long *)(PTR_DAT_019e4d88 + 8);
  uVar3 = FUN_000e8680(lVar2,0,0xffffffff);
  thunk_FUN_012aa986(param_1,0,uVar3);
  uVar5 = *(ushort *)(lVar2 + 0x1c) & 0x78;
  bVar7 = uVar5 != 0;
  if (uVar5 == 0) {
    uVar6 = *(uint *)(lVar2 + 0x20);
    if ((*(ushort *)(lVar2 + 0x1c) & 0x40) != 0) {
      if ((param_1 == (ulong *)0x0) || (lVar4 = FUN_000e8a90(lVar2,param_1), lVar4 == 0)) {
        uVar6 = uVar6 | 0x5488bf;
      }
      else {
        uVar6 = uVar6 | *(uint *)(lVar4 + 0x20) & 0x5488bf;
      }
    }
    bVar7 = (uVar6 & 0xc08070) != 0;
  }
  if (bVar7) {
    FUN_000e6730(lVar2,param_1,0,0xffffffff,0);
  }
  lVar2 = *(long *)(PTR_DAT_019e4d90 + 8);
  uVar3 = FUN_000e8680(lVar2,0,0xffffffff);
  puVar1 = param_1 + 6;
  thunk_FUN_012aa986(puVar1,0,uVar3);
  uVar5 = *(ushort *)(lVar2 + 0x1c) & 0x78;
  bVar7 = uVar5 != 0;
  if (uVar5 == 0) {
    uVar6 = *(uint *)(lVar2 + 0x20);
    if ((*(ushort *)(lVar2 + 0x1c) & 0x40) != 0) {
      lVar4 = FUN_000e8a90(lVar2,puVar1);
      if (lVar4 == 0) {
        uVar6 = uVar6 | 0x5488bf;
      }
      else {
        uVar6 = *(uint *)(lVar4 + 0x20) & 0x5488bf | uVar6;
      }
    }
    bVar7 = (uVar6 & 0xc08070) != 0;
  }
  if (bVar7) {
    FUN_000e6730(lVar2,puVar1,0,0xffffffff,0);
  }
  lVar2 = *(long *)(PTR_DAT_019e4d80 + 8);
  uVar3 = FUN_000e8680(lVar2,0,0xffffffff);
  thunk_FUN_012aa986(local_60,0,uVar3);
  uVar5 = *(ushort *)(lVar2 + 0x1c) & 0x78;
  bVar7 = uVar5 != 0;
  if (uVar5 == 0) {
    uVar6 = *(uint *)(lVar2 + 0x20);
    if ((*(ushort *)(lVar2 + 0x1c) & 0x40) != 0) {
      lVar4 = FUN_000e8a90(lVar2,local_60);
      if (lVar4 == 0) {
        uVar6 = uVar6 | 0x5488bf;
      }
      else {
        uVar6 = *(uint *)(lVar4 + 0x20) & 0x5488bf | uVar6;
      }
    }
    bVar7 = (uVar6 & 0xc08070) != 0;
  }
  if (bVar7) {
    FUN_000e6730(lVar2,local_60,0,0xffffffff,0);
  }
  local_60[1] = 0;
  local_60[2] = 0;
  local_60[3] = 0;
  local_60[4] = 0;
  local_60[5] = 0;
  local_60[6] = 0;
  local_60[7] = 0;
  local_60[8] = 0;
  param_1[5] = local_38;
  param_1[4] = local_40;
  param_1[3] = local_48;
  param_1[2] = local_50;
  param_1[1] = (ulong)uStack_57 << 8;
  *param_1 = (ulong)local_60[0];
  FUN_0058bcf0(puVar1);
  lVar2 = *(long *)(PTR_DAT_019e4d60 + 8);
  uVar3 = FUN_000e8680(lVar2,0,0xffffffff);
  puVar1 = param_1 + 9;
  thunk_FUN_012aa986(puVar1,0,uVar3);
  uVar5 = *(ushort *)(lVar2 + 0x1c) & 0x78;
  bVar7 = uVar5 != 0;
  if (uVar5 == 0) {
    uVar6 = *(uint *)(lVar2 + 0x20);
    if ((*(ushort *)(lVar2 + 0x1c) & 0x40) != 0) {
      lVar4 = FUN_000e8a90(lVar2,puVar1);
      if (lVar4 == 0) {
        uVar6 = uVar6 | 0x5488bf;
      }
      else {
        uVar6 = *(uint *)(lVar4 + 0x20) & 0x5488bf | uVar6;
      }
    }
    bVar7 = (uVar6 & 0xc08070) != 0;
  }
  if (bVar7) {
    FUN_000e6730(lVar2,puVar1,0,0xffffffff,0);
  }
  *(undefined2 *)((long)param_1 + 0x41c) = 0;
  *(undefined1 *)((long)param_1 + 0x41e) = 1;
  if (*DAT_01a1f100 != local_30) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

