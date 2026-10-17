
void FUN_001d9520(undefined8 *param_1)

{
  long lVar1;
  undefined8 uVar2;
  long lVar3;
  ushort uVar4;
  uint uVar5;
  bool bVar6;
  
  *param_1 = 0x811c9dc5811c9dc5;
  *(undefined4 *)(param_1 + 1) = 0x811c9dc5;
  lVar1 = *(long *)(PTR_DAT_0191a1c0 + 8);
  uVar2 = FUN_000e8680(lVar1,0,0xffffffff);
  thunk_FUN_012aa986(param_1,0,uVar2);
  uVar4 = *(ushort *)(lVar1 + 0x1c) & 0x78;
  bVar6 = uVar4 != 0;
  if (uVar4 != 0) goto LAB_001d95b8;
  uVar5 = *(uint *)(lVar1 + 0x20);
  if ((*(ushort *)(lVar1 + 0x1c) & 0x40) != 0) {
    if (param_1 != (undefined8 *)0x0) {
      lVar3 = FUN_000e8a90(lVar1,param_1);
      if (lVar3 != 0) {
        uVar5 = uVar5 | *(uint *)(lVar3 + 0x20) & 0x5488bf;
        goto LAB_001d95af;
      }
    }
    uVar5 = uVar5 | 0x5488bf;
  }
LAB_001d95af:
  bVar6 = (uVar5 & 0xc08070) != 0;
LAB_001d95b8:
  if (bVar6) {
    FUN_000e6730(lVar1,param_1,0,0xffffffff,0);
    return;
  }
  return;
}

