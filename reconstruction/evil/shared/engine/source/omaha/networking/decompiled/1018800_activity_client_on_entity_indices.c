
undefined8 FUN_01018800(long *param_1,undefined8 param_2,undefined4 param_3)

{
  undefined *puVar1;
  char cVar2;
  undefined8 uVar3;
  long lVar4;
  long lVar5;
  uint uVar6;
  ushort uVar7;
  undefined1 uVar8;
  bool bVar9;
  uint local_638 [384];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  thunk_FUN_012aa986(local_638,0,0x600);
  puVar1 = PTR_DAT_0191a3a0;
  lVar5 = *(long *)(PTR_DAT_0191a3a0 + 8);
  uVar3 = FUN_000e8680(lVar5,0,0xffffffff);
  thunk_FUN_012aa986(local_638,0,uVar3);
  uVar7 = *(ushort *)(lVar5 + 0x1c) & 0x78;
  bVar9 = uVar7 != 0;
  if (uVar7 == 0) {
    uVar6 = *(uint *)(lVar5 + 0x20);
    if ((*(ushort *)(lVar5 + 0x1c) & 0x40) != 0) {
      lVar4 = FUN_000e8a90(lVar5,local_638);
      if (lVar4 == 0) {
        uVar6 = uVar6 | 0x5488bf;
      }
      else {
        uVar6 = *(uint *)(lVar4 + 0x20) & 0x5488bf | uVar6;
      }
    }
    bVar9 = (uVar6 & 0xc08070) != 0;
  }
  if (bVar9) {
    FUN_000e6730(lVar5,local_638,0,0xffffffff,0);
  }
  (**(code **)(*param_1 + 0x38))(param_1);
  cVar2 = FUN_002a4ac0(*(undefined4 *)puVar1,param_2,param_3,local_638);
  uVar8 = 0;
  if (cVar2 != '\0') {
    *(undefined2 *)(param_1 + 0xc95) = 1;
    *(undefined1 *)((long)param_1 + 0x64aa) = 1;
    lVar5 = 0;
    do {
      *(uint *)((long)param_1 + (long)(&DAT_00005ea8 + lVar5 * 4)) =
           *(uint *)((long)param_1 + (long)(&DAT_00005ea8 + lVar5 * 4)) | local_638[lVar5];
      lVar5 = lVar5 + 1;
    } while ((int)lVar5 != 0x180);
    uVar8 = 1;
    if ((char)param_1[0xc95] != '\0') {
      uVar3 = (**(code **)(*param_1 + 0x10))(param_1);
      FUN_00240a40(uVar3);
      *(undefined1 *)(param_1 + 0xc95) = 0;
    }
  }
  if (*DAT_01a1f100 != local_38) {
    uVar3 = thunk_FUN_012aa7f6();
    return uVar3;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar8);
}

