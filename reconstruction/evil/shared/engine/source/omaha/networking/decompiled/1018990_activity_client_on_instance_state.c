
bool FUN_01018990(long *param_1,undefined8 param_2,undefined4 param_3)

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
  undefined1 local_6e8 [88];
  undefined4 local_690;
  undefined4 local_684;
  undefined4 local_680;
  undefined4 local_668;
  undefined4 local_650;
  undefined4 local_638;
  undefined4 local_620;
  undefined4 local_608;
  undefined4 local_5f0;
  undefined4 local_5d8;
  undefined4 local_5c0;
  undefined4 local_5a8;
  undefined4 local_590;
  undefined4 local_578;
  undefined4 local_560;
  undefined4 local_548;
  undefined4 local_530;
  undefined4 local_518;
  undefined4 local_500;
  undefined4 local_4e8;
  undefined4 local_4d0;
  undefined4 local_4b8;
  undefined4 local_4a0;
  undefined4 local_488;
  undefined4 local_470;
  undefined4 local_458;
  undefined4 local_440;
  undefined4 local_428;
  undefined4 local_410;
  undefined4 local_3f8;
  undefined4 local_3e0;
  undefined4 local_3c8;
  undefined4 local_3b0;
  undefined4 local_398;
  undefined4 local_380;
  undefined4 local_368;
  undefined4 local_350;
  undefined4 local_338;
  undefined4 local_320;
  undefined4 local_308;
  undefined4 local_2f0;
  undefined4 local_2d8;
  undefined4 local_2c0;
  undefined4 local_2a8;
  undefined4 local_290;
  undefined4 local_278;
  undefined4 local_260;
  undefined4 local_248;
  undefined4 local_230;
  undefined4 local_218;
  undefined4 local_200;
  undefined4 local_1e8;
  undefined4 local_1d0;
  undefined4 local_1c0;
  undefined4 local_ec;
  long local_38;
  
  puVar2 = PTR_DAT_0191a410;
  local_38 = *DAT_01a1f100;
  local_690 = 0x811c9dc5;
  local_684 = 0;
  local_680 = 0x811c9dc5;
  local_668 = 0x811c9dc5;
  local_650 = 0x811c9dc5;
  local_638 = 0x811c9dc5;
  local_620 = 0x811c9dc5;
  local_608 = 0x811c9dc5;
  local_5f0 = 0x811c9dc5;
  local_5d8 = 0x811c9dc5;
  local_5c0 = 0x811c9dc5;
  local_5a8 = 0x811c9dc5;
  local_590 = 0x811c9dc5;
  local_578 = 0x811c9dc5;
  local_560 = 0x811c9dc5;
  local_548 = 0x811c9dc5;
  local_530 = 0x811c9dc5;
  local_518 = 0x811c9dc5;
  local_500 = 0x811c9dc5;
  local_4e8 = 0x811c9dc5;
  local_4d0 = 0x811c9dc5;
  local_4b8 = 0x811c9dc5;
  local_4a0 = 0x811c9dc5;
  local_488 = 0x811c9dc5;
  local_470 = 0x811c9dc5;
  local_458 = 0x811c9dc5;
  local_440 = 0x811c9dc5;
  local_428 = 0x811c9dc5;
  local_410 = 0x811c9dc5;
  local_3f8 = 0x811c9dc5;
  local_3e0 = 0x811c9dc5;
  local_3c8 = 0x811c9dc5;
  local_3b0 = 0x811c9dc5;
  local_398 = 0x811c9dc5;
  local_380 = 0x811c9dc5;
  local_368 = 0x811c9dc5;
  local_350 = 0x811c9dc5;
  local_338 = 0x811c9dc5;
  local_320 = 0x811c9dc5;
  local_308 = 0x811c9dc5;
  local_2f0 = 0x811c9dc5;
  local_2d8 = 0x811c9dc5;
  local_2c0 = 0x811c9dc5;
  local_2a8 = 0x811c9dc5;
  local_290 = 0x811c9dc5;
  local_278 = 0x811c9dc5;
  local_260 = 0x811c9dc5;
  local_248 = 0x811c9dc5;
  local_230 = 0x811c9dc5;
  local_218 = 0x811c9dc5;
  local_200 = 0x811c9dc5;
  local_1e8 = 0x811c9dc5;
  local_1d0 = 0x811c9dc5;
  local_1c0 = 0;
  local_ec = 0;
  lVar1 = *(long *)(PTR_DAT_0191a410 + 8);
  uVar5 = FUN_000e8680(lVar1,0,0xffffffff);
  thunk_FUN_012aa986(local_6e8,0,uVar5);
  uVar8 = *(ushort *)(lVar1 + 0x1c) & 0x78;
  bVar9 = uVar8 != 0;
  if (uVar8 == 0) {
    uVar7 = *(uint *)(lVar1 + 0x20);
    if ((*(ushort *)(lVar1 + 0x1c) & 0x40) != 0) {
      lVar6 = FUN_000e8a90(lVar1,local_6e8);
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
    FUN_000e6730(lVar1,local_6e8,0,0xffffffff,0);
  }
  (**(code **)(*param_1 + 0x38))(param_1);
  cVar3 = FUN_002a4ac0(*(undefined4 *)puVar2,param_2,param_3,local_6e8);
  if (cVar3 != '\0') {
    uVar5 = (**(code **)(*param_1 + 0x10))(param_1);
    FUN_002409c0(uVar5,local_6e8);
    *(byte *)(param_1 + 0x26) = *(byte *)(param_1 + 0x26) | 0x40;
  }
  if (*DAT_01a1f100 != local_38) {
    uVar4 = thunk_FUN_012aa7f6();
    return (bool)uVar4;
  }
  return cVar3 != '\0';
}

