
undefined8 FUN_010190f0(long *param_1,undefined8 param_2,undefined4 param_3)

{
  long lVar1;
  undefined *puVar2;
  char cVar3;
  undefined8 uVar4;
  long lVar5;
  uint uVar6;
  ushort uVar7;
  bool bVar8;
  undefined1 local_640 [4];
  undefined1 local_63c [1540];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  thunk_FUN_012aa986(local_63c,0,0x600);
  puVar2 = PTR_DAT_0191a3c8;
  lVar1 = *(long *)(PTR_DAT_0191a3c8 + 8);
  uVar4 = FUN_000e8680(lVar1,0,0xffffffff);
  thunk_FUN_012aa986(local_640,0,uVar4);
  uVar7 = *(ushort *)(lVar1 + 0x1c) & 0x78;
  bVar8 = uVar7 != 0;
  if (uVar7 == 0) {
    uVar6 = *(uint *)(lVar1 + 0x20);
    if ((*(ushort *)(lVar1 + 0x1c) & 0x40) != 0) {
      lVar5 = FUN_000e8a90(lVar1,local_640);
      if (lVar5 == 0) {
        uVar6 = uVar6 | 0x5488bf;
      }
      else {
        uVar6 = *(uint *)(lVar5 + 0x20) & 0x5488bf | uVar6;
      }
    }
    bVar8 = (uVar6 & 0xc08070) != 0;
  }
  if (bVar8) {
    FUN_000e6730(lVar1,local_640,0,0xffffffff,0);
  }
  (**(code **)(*param_1 + 0x38))(param_1);
  cVar3 = FUN_002a4ac0(*(undefined4 *)puVar2,param_2,param_3,local_640);
  uVar4 = 0;
  if (cVar3 != '\0') {
    uVar7 = *(ushort *)(param_1 + 0x26);
    if ((uVar7 & 0x200) == 0) {
      uVar4 = (**(code **)(*param_1 + 0x10))(param_1);
      cVar3 = FUN_00240910(uVar4,local_640);
      uVar4 = 1;
      if (cVar3 != '\0') goto LAB_0101923e;
      uVar7 = *(ushort *)(param_1 + 0x26);
    }
    *(ushort *)(param_1 + 0x26) = uVar7 | 0x200;
    uVar4 = 0;
  }
LAB_0101923e:
  if (*DAT_01a1f100 != local_38) {
    uVar4 = thunk_FUN_012aa7f6();
    return uVar4;
  }
  return uVar4;
}

