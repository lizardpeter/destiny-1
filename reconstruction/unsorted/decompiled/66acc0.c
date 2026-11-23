
void FUN_0066acc0(long param_1)

{
  long lVar1;
  undefined8 uVar2;
  long lVar3;
  ushort uVar4;
  uint uVar5;
  bool bVar6;
  
  lVar1 = *(long *)(PTR_DAT_019b1ba0 + 8);
  uVar2 = FUN_000e8680(lVar1,0,0xffffffff);
  thunk_FUN_012aa986(param_1,0,uVar2);
  uVar4 = *(ushort *)(lVar1 + 0x1c) & 0x78;
  bVar6 = uVar4 != 0;
  if (uVar4 != 0) goto LAB_0066ad43;
  uVar5 = *(uint *)(lVar1 + 0x20);
  if ((*(ushort *)(lVar1 + 0x1c) & 0x40) != 0) {
    if (param_1 != 0) {
      lVar3 = FUN_000e8a90(lVar1,param_1);
      if (lVar3 != 0) {
        uVar5 = uVar5 | *(uint *)(lVar3 + 0x20) & 0x5488bf;
        goto LAB_0066ad3a;
      }
    }
    uVar5 = uVar5 | 0x5488bf;
  }
LAB_0066ad3a:
  bVar6 = (uVar5 & 0xc08070) != 0;
LAB_0066ad43:
  if (bVar6) {
    FUN_000e6730(lVar1,param_1,0,0xffffffff,0);
    return;
  }
  return;
}

