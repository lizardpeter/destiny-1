
bool FUN_01018d00(long *param_1,undefined8 param_2,undefined4 param_3)

{
  long lVar1;
  undefined *puVar2;
  char cVar3;
  undefined1 uVar4;
  undefined8 uVar5;
  long lVar6;
  uint uVar7;
  ushort uVar8;
  bool bVar9;
  undefined1 local_40 [8];
  long local_38;
  
  puVar2 = PTR_DAT_0191a418;
  local_38 = *DAT_01a1f100;
  lVar1 = *(long *)(PTR_DAT_0191a418 + 8);
  uVar5 = FUN_000e8680(lVar1,0,0xffffffff);
  thunk_FUN_012aa986(local_40,0,uVar5);
  uVar8 = *(ushort *)(lVar1 + 0x1c) & 0x78;
  bVar9 = uVar8 != 0;
  if (uVar8 == 0) {
    uVar7 = *(uint *)(lVar1 + 0x20);
    if ((*(ushort *)(lVar1 + 0x1c) & 0x40) != 0) {
      lVar6 = FUN_000e8a90(lVar1,local_40);
      if (lVar6 == 0) {
        uVar7 = uVar7 | 0x5488bf;
      }
      else {
        uVar7 = *(uint *)(lVar6 + 0x20) & 0x5488bf | uVar7;
      }
    }
    bVar9 = (uVar7 & 0xc08070) != 0;
  }
  if (bVar9) {
    FUN_000e6730(lVar1,local_40,0,0xffffffff,0);
  }
  (**(code **)(*param_1 + 0x38))(param_1);
  cVar3 = FUN_002a4ac0(*(undefined4 *)puVar2,param_2,param_3,local_40);
  if (cVar3 != '\0') {
    uVar5 = (**(code **)(*param_1 + 0x10))(param_1);
    FUN_002409e0(uVar5,local_40);
    *(byte *)(param_1 + 0x26) = *(byte *)(param_1 + 0x26) | 0x80;
  }
  if (*DAT_01a1f100 != local_38) {
    uVar4 = thunk_FUN_012aa7f6();
    return (bool)uVar4;
  }
  return cVar3 != '\0';
}

