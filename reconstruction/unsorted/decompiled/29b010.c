
undefined8 FUN_0029b010(long *param_1,undefined4 *param_2)

{
  long lVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  int iVar6;
  undefined4 uVar7;
  undefined8 uVar8;
  long lVar9;
  undefined8 uVar10;
  uint uVar11;
  ushort uVar12;
  undefined *puVar13;
  undefined *puVar14;
  bool bVar15;
  undefined4 *puVar16;
  undefined4 uVar17;
  undefined4 local_190 [80];
  undefined1 local_50 [4];
  undefined4 local_4c;
  long local_48;
  undefined4 local_40;
  long local_38;
  
  puVar13 = PTR_DAT_0191a390;
  local_38 = *DAT_01a1f100;
  local_40 = 0x811c9dc5;
  lVar1 = *(long *)(PTR_DAT_0191a390 + 8);
  uVar8 = FUN_000e8680(lVar1,0,0xffffffff);
  thunk_FUN_012aa986(local_50,0,uVar8);
  uVar12 = *(ushort *)(lVar1 + 0x1c) & 0x78;
  bVar15 = uVar12 != 0;
  if (uVar12 == 0) {
    uVar11 = *(uint *)(lVar1 + 0x20);
    if ((*(ushort *)(lVar1 + 0x1c) & 0x40) != 0) {
      lVar9 = FUN_000e8a90(lVar1,local_50);
      if (lVar9 == 0) {
        uVar11 = uVar11 | 0x5488bf;
      }
      else {
        uVar11 = *(uint *)(lVar9 + 0x20) & 0x5488bf | uVar11;
      }
    }
    bVar15 = (uVar11 & 0xc08070) != 0;
  }
  if (bVar15) {
    FUN_000e6730(lVar1,local_50,0,0xffffffff,0);
  }
  local_4c = FUN_00057e60();
  local_48 = param_1[0x1cd];
  local_40 = *param_2;
  uVar8 = (**(code **)(*param_1 + 0x10))(param_1);
  puVar16 = local_190;
  local_190[0] = 0;
  cVar2 = FUN_00299d10(param_1,uVar8,0xe,*(undefined4 *)puVar13,local_50,0x14,puVar16);
  uVar17 = (undefined4)((ulong)puVar16 >> 0x20);
  if (cVar2 == '\0') {
    if ((DAT_02655498 == '\0') && (iVar6 = thunk_FUN_012aa7d6(&DAT_02655498), iVar6 != 0)) {
      DAT_02655490 = FUN_000e4a10(s_networking_activity_client___AC___016221a9);
      thunk_FUN_012aa7e6(&DAT_02655498);
    }
    cVar3 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
    cVar4 = (**(code **)(*param_1 + 0x18))(param_1);
    cVar5 = (**(code **)(*param_1 + 0x18))(param_1);
    puVar13 = &DAT_01621de5;
    puVar14 = &DAT_01621de5;
    if (cVar3 != '\0') {
      puVar14 = &DAT_01621de3;
    }
    if (cVar4 != '\0') {
      puVar13 = &DAT_01621de3;
    }
    if (cVar5 == '\0') {
      uVar8 = FUN_00001df0();
    }
    else {
      uVar8 = (**(code **)(*param_1 + 0x10))(param_1);
    }
    uVar7 = FUN_00057e60(param_1 + 0x1ce);
    uVar10 = FUN_00068600(param_1 + 0x1cd);
    FUN_01008290(local_190,s_networking_activity_client___AC___016221a9,param_1 + 4,puVar14,puVar13,
                 uVar8,CONCAT44(uVar17,uVar7),uVar10);
    FUN_000e4aa0(DAT_02655490,local_190);
  }
  if (*DAT_01a1f100 != local_38) {
    uVar8 = thunk_FUN_012aa7f6();
    return uVar8;
  }
  return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),cVar2);
}

