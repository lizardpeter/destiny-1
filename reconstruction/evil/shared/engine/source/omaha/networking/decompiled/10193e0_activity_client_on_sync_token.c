
ulong FUN_010193e0(long *param_1,undefined8 param_2,undefined4 param_3)

{
  long lVar1;
  undefined *puVar2;
  undefined8 uVar3;
  long lVar4;
  ulong uVar5;
  ulong uVar6;
  uint uVar7;
  ushort uVar8;
  bool bVar9;
  undefined4 local_40 [2];
  long local_38;
  
  puVar2 = PTR_DAT_0191a3e0;
  local_38 = *DAT_01a1f100;
  lVar1 = *(long *)(PTR_DAT_0191a3e0 + 8);
  uVar3 = FUN_000e8680(lVar1,0,0xffffffff);
  thunk_FUN_012aa986(local_40,0,uVar3);
  uVar8 = *(ushort *)(lVar1 + 0x1c) & 0x78;
  bVar9 = uVar8 != 0;
  if (uVar8 == 0) {
    uVar7 = *(uint *)(lVar1 + 0x20);
    if ((*(ushort *)(lVar1 + 0x1c) & 0x40) != 0) {
      lVar4 = FUN_000e8a90(lVar1,local_40);
      if (lVar4 == 0) {
        uVar7 = uVar7 | 0x5488bf;
      }
      else {
        uVar7 = *(uint *)(lVar4 + 0x20) & 0x5488bf | uVar7;
      }
    }
    bVar9 = (uVar7 & 0xc08070) != 0;
  }
  if (bVar9) {
    FUN_000e6730(lVar1,local_40,0,0xffffffff,0);
  }
  (**(code **)(*param_1 + 0x38))(param_1);
  uVar5 = FUN_002a4ac0(*(undefined4 *)puVar2,param_2,param_3,local_40);
  uVar6 = uVar5 & 0xffffffffffffff00;
  if ((char)uVar5 != '\0') {
    *(undefined4 *)((long)param_1 + 0x64ac) = local_40[0];
    uVar6 = CONCAT71((uint7)(uint3)((uint)local_40[0] >> 8),1);
  }
  if (*DAT_01a1f100 != local_38) {
    uVar5 = thunk_FUN_012aa7f6();
    return uVar5;
  }
  return uVar6;
}

