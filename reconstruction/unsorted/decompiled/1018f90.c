
undefined8 FUN_01018f90(long *param_1,undefined8 param_2,undefined4 param_3)

{
  long lVar1;
  undefined *puVar2;
  char cVar3;
  undefined8 uVar4;
  long lVar5;
  uint uVar6;
  ushort uVar7;
  undefined1 uVar8;
  bool bVar9;
  undefined1 local_308 [720];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_00254730(local_308);
  puVar2 = PTR_DAT_0191a360;
  lVar1 = *(long *)(PTR_DAT_0191a360 + 8);
  uVar4 = FUN_000e8680(lVar1,0,0xffffffff);
  thunk_FUN_012aa986(local_308,0,uVar4);
  uVar7 = *(ushort *)(lVar1 + 0x1c) & 0x78;
  bVar9 = uVar7 != 0;
  if (uVar7 == 0) {
    uVar6 = *(uint *)(lVar1 + 0x20);
    if ((*(ushort *)(lVar1 + 0x1c) & 0x40) != 0) {
      lVar5 = FUN_000e8a90(lVar1,local_308);
      if (lVar5 == 0) {
        uVar6 = uVar6 | 0x5488bf;
      }
      else {
        uVar6 = *(uint *)(lVar5 + 0x20) & 0x5488bf | uVar6;
      }
    }
    bVar9 = (uVar6 & 0xc08070) != 0;
  }
  if (bVar9) {
    FUN_000e6730(lVar1,local_308,0,0xffffffff,0);
  }
  (**(code **)(*param_1 + 0x38))(param_1);
  cVar3 = FUN_002a4ac0(*(undefined4 *)puVar2,param_2,param_3,local_308);
  uVar8 = 0;
  if (cVar3 != '\0') {
    cVar3 = FUN_002592d0();
    uVar8 = 1;
    if ((cVar3 != '\0') && (cVar3 = (**(code **)(*param_1 + 0x18))(param_1), cVar3 != '\0')) {
      uVar4 = (**(code **)(*param_1 + 0x10))(param_1);
      FUN_00240940(uVar4,local_308);
    }
  }
  if (*DAT_01a1f100 != local_38) {
    uVar4 = thunk_FUN_012aa7f6();
    return uVar4;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar8);
}

