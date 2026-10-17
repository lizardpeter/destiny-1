
void FUN_002a2620(long param_1)

{
  long lVar1;
  undefined8 uVar2;
  long lVar3;
  long lVar4;
  uint uVar5;
  ushort uVar6;
  bool bVar7;
  
  *(undefined1 *)(param_1 + 4) = 0;
  *(undefined1 *)(param_1 + 5) = 0;
  *(undefined4 *)(param_1 + 0x38) = 0xffffffff;
  *(undefined8 *)(param_1 + 0x5c) = 0;
  *(undefined8 *)(param_1 + 0x54) = 0;
  lVar4 = *(long *)(PTR_DAT_0191a238 + 8);
  uVar2 = FUN_000e8680(lVar4,0,0xffffffff);
  lVar1 = param_1 + 0x50b0;
  thunk_FUN_012aa986(lVar1,0,uVar2);
  uVar6 = *(ushort *)(lVar4 + 0x1c) & 0x78;
  bVar7 = uVar6 != 0;
  if (uVar6 == 0) {
    uVar5 = *(uint *)(lVar4 + 0x20);
    if ((*(ushort *)(lVar4 + 0x1c) & 0x40) != 0) {
      lVar3 = FUN_000e8a90(lVar4,lVar1);
      if (lVar3 == 0) {
        uVar5 = uVar5 | 0x5488bf;
      }
      else {
        uVar5 = *(uint *)(lVar3 + 0x20) & 0x5488bf | uVar5;
      }
    }
    bVar7 = (uVar5 & 0xc08070) != 0;
  }
  if (bVar7) {
    FUN_000e6730(lVar4,lVar1,0,0xffffffff,0);
  }
  lVar4 = *(long *)(PTR_DAT_0191a2e0 + 8);
  uVar2 = FUN_000e8680(lVar4,0,0xffffffff);
  lVar1 = param_1 + 0x1c;
  thunk_FUN_012aa986(lVar1,0,uVar2);
  uVar6 = *(ushort *)(lVar4 + 0x1c) & 0x78;
  bVar7 = uVar6 != 0;
  if (uVar6 == 0) {
    uVar5 = *(uint *)(lVar4 + 0x20);
    if ((*(ushort *)(lVar4 + 0x1c) & 0x40) != 0) {
      lVar3 = FUN_000e8a90(lVar4,lVar1);
      if (lVar3 == 0) {
        uVar5 = uVar5 | 0x5488bf;
      }
      else {
        uVar5 = *(uint *)(lVar3 + 0x20) & 0x5488bf | uVar5;
      }
    }
    bVar7 = (uVar5 & 0xc08070) != 0;
  }
  if (bVar7) {
    FUN_000e6730(lVar4,lVar1,0,0xffffffff,0);
  }
  lVar1 = *(long *)(PTR_DAT_0191a2e8 + 8);
  uVar2 = FUN_000e8680(lVar1,0,0xffffffff);
  param_1 = param_1 + 0x24;
  thunk_FUN_012aa986(param_1,0,uVar2);
  uVar6 = *(ushort *)(lVar1 + 0x1c) & 0x78;
  bVar7 = uVar6 != 0;
  if (uVar6 == 0) {
    uVar5 = *(uint *)(lVar1 + 0x20);
    if ((*(ushort *)(lVar1 + 0x1c) & 0x40) != 0) {
      lVar4 = FUN_000e8a90(lVar1,param_1);
      if (lVar4 == 0) {
        uVar5 = uVar5 | 0x5488bf;
      }
      else {
        uVar5 = *(uint *)(lVar4 + 0x20) & 0x5488bf | uVar5;
      }
    }
    bVar7 = (uVar5 & 0xc08070) != 0;
  }
  if (!bVar7) {
    return;
  }
  FUN_000e6730(lVar1,param_1,0,0xffffffff,0);
  return;
}

