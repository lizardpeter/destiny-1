
void FUN_0057cbf0(long param_1)

{
  long lVar1;
  undefined8 uVar2;
  long lVar3;
  long lVar4;
  ushort uVar5;
  uint uVar6;
  bool bVar7;
  
  lVar1 = *(long *)(PTR_DAT_019e4d08 + 8);
  uVar2 = FUN_000e8680(lVar1,0,0xffffffff);
  thunk_FUN_012aa986(param_1,0,uVar2);
  uVar5 = *(ushort *)(lVar1 + 0x1c) & 0x78;
  bVar7 = uVar5 != 0;
  if (uVar5 == 0) {
    uVar6 = *(uint *)(lVar1 + 0x20);
    if ((*(ushort *)(lVar1 + 0x1c) & 0x40) != 0) {
      if ((param_1 == 0) || (lVar3 = FUN_000e8a90(lVar1,param_1), lVar3 == 0)) {
        uVar6 = uVar6 | 0x5488bf;
      }
      else {
        uVar6 = uVar6 | *(uint *)(lVar3 + 0x20) & 0x5488bf;
      }
    }
    bVar7 = (uVar6 & 0xc08070) != 0;
  }
  if (bVar7) {
    FUN_000e6730(lVar1,param_1,0,0xffffffff,0);
  }
  lVar3 = *(long *)(PTR_DAT_019e4d10 + 8);
  uVar2 = FUN_000e8680(lVar3,0,0xffffffff);
  lVar1 = param_1 + 0x150;
  thunk_FUN_012aa986(lVar1,0,uVar2);
  uVar5 = *(ushort *)(lVar3 + 0x1c) & 0x78;
  bVar7 = uVar5 != 0;
  if (uVar5 == 0) {
    uVar6 = *(uint *)(lVar3 + 0x20);
    if ((*(ushort *)(lVar3 + 0x1c) & 0x40) != 0) {
      lVar4 = FUN_000e8a90(lVar3,lVar1);
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
    FUN_000e6730(lVar3,lVar1,0,0xffffffff,0);
  }
  FUN_0058bcf0(lVar1);
  FUN_0058bcf0(param_1 + 0x168);
  FUN_0058bcf0(param_1 + 0x180);
  FUN_0058bcf0(param_1 + 0x198);
  FUN_0058bcf0(param_1 + 0x1b0);
  FUN_0058bcf0(param_1 + 0x1c8);
  FUN_0058bcf0(param_1 + 0x1e0);
  FUN_0058bcf0(param_1 + 0x1f8);
  FUN_0058bcf0(param_1 + 0x210);
  FUN_0058bcf0(param_1 + 0x228);
  FUN_0058bcf0(param_1 + 0x240);
  FUN_0058bcf0(param_1 + 600);
  FUN_0058bcf0(param_1 + 0x270);
  FUN_0058bcf0(param_1 + 0x288);
  FUN_0058bcf0(param_1 + 0x2a0);
  FUN_0058bcf0(param_1 + 0x2b8);
  FUN_0058bcf0(param_1 + 0x2d0);
  FUN_0058bcf0(param_1 + 0x2e8);
  FUN_0058bcf0(param_1 + 0x300);
  FUN_0058bcf0(param_1 + 0x318);
  FUN_00543ee0(param_1 + 0x330);
  return;
}

