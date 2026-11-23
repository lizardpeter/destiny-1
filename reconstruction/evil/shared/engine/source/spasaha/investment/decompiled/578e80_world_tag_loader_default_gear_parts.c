
undefined8 FUN_00578e80(long param_1,undefined1 param_2,undefined8 param_3)

{
  undefined8 uVar1;
  long lVar2;
  long *plVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  long lVar6;
  long lVar7;
  bool bVar8;
  uint uVar9;
  ushort uVar10;
  long lVar11;
  long lVar12;
  long lVar13;
  bool bVar14;
  undefined1 local_bb8 [8];
  undefined1 local_bb0 [204];
  undefined4 local_ae4;
  undefined4 local_ae0;
  undefined4 local_adc;
  undefined4 local_ad8;
  undefined4 local_ad4;
  undefined4 local_ad0;
  undefined4 local_acc;
  undefined4 local_ac8;
  undefined4 local_ac4;
  undefined4 local_ac0;
  undefined4 local_ab8;
  undefined4 local_ab0;
  undefined4 local_aa8;
  undefined4 local_aa0;
  undefined4 local_a98;
  undefined4 local_a90;
  undefined4 local_a88;
  undefined1 local_a80 [24];
  undefined4 local_a68;
  undefined4 local_a48;
  undefined4 local_a28;
  undefined4 local_a08;
  undefined4 local_9e8;
  undefined4 local_9c8;
  undefined4 local_9a8;
  undefined4 local_988;
  undefined4 local_980;
  undefined4 local_97c;
  undefined4 local_978;
  undefined4 local_974;
  undefined4 local_970;
  undefined4 local_96c;
  undefined4 local_968;
  undefined4 local_964;
  undefined4 local_960;
  undefined1 local_958 [4];
  undefined4 local_954;
  undefined1 local_938 [4];
  undefined4 local_934;
  undefined1 local_918 [4];
  undefined4 local_914;
  undefined1 local_8f8 [4];
  undefined4 local_8f4;
  undefined1 local_8d8 [4];
  undefined4 local_8d4;
  undefined4 local_8b4;
  undefined4 local_894;
  undefined4 local_874;
  undefined4 local_854;
  undefined4 local_834;
  undefined4 local_814;
  undefined4 local_7f4;
  undefined4 local_7d4;
  undefined1 local_7b8 [32];
  undefined4 local_798;
  undefined1 auStack_790 [56];
  undefined4 local_758;
  undefined4 local_718;
  undefined4 local_6d8;
  undefined4 local_698;
  undefined4 local_658;
  undefined4 local_618;
  undefined4 local_5d8;
  undefined4 local_598;
  undefined4 local_558;
  undefined4 local_518;
  undefined4 local_4d8;
  undefined4 local_498;
  undefined4 local_458;
  undefined4 local_418;
  undefined4 local_3d8;
  undefined4 local_398;
  undefined4 local_358;
  undefined4 local_318;
  undefined4 local_2d8;
  undefined1 local_2b8 [640];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar1 = FUN_005494c0();
  lVar2 = FUN_0054b0c0(uVar1);
  uVar1 = FUN_005494c0();
  plVar3 = (long *)FUN_0025a550();
  uVar4 = (**(code **)(*plVar3 + 0x68))(plVar3);
  thunk_FUN_012aa986(local_2b8,0xff,0x280);
  local_798 = 0x811c9dc5;
  local_758 = 0x811c9dc5;
  local_718 = 0x811c9dc5;
  local_6d8 = 0x811c9dc5;
  local_698 = 0x811c9dc5;
  local_658 = 0x811c9dc5;
  local_618 = 0x811c9dc5;
  local_5d8 = 0x811c9dc5;
  local_598 = 0x811c9dc5;
  local_558 = 0x811c9dc5;
  local_518 = 0x811c9dc5;
  local_4d8 = 0x811c9dc5;
  local_498 = 0x811c9dc5;
  local_458 = 0x811c9dc5;
  local_418 = 0x811c9dc5;
  local_3d8 = 0x811c9dc5;
  local_398 = 0x811c9dc5;
  local_358 = 0x811c9dc5;
  local_318 = 0x811c9dc5;
  local_2d8 = 0x811c9dc5;
  lVar11 = *(long *)(PTR_DAT_0197e2c0 + 8);
  uVar5 = FUN_000e8680(lVar11,0,0xffffffff);
  thunk_FUN_012aa986(local_7b8,0,uVar5);
  uVar10 = *(ushort *)(lVar11 + 0x1c) & 0x78;
  bVar14 = uVar10 != 0;
  if (uVar10 == 0) {
    uVar9 = *(uint *)(lVar11 + 0x20);
    if ((*(ushort *)(lVar11 + 0x1c) & 0x40) != 0) {
      lVar6 = FUN_000e8a90(lVar11,local_7b8);
      if (lVar6 == 0) {
        uVar9 = uVar9 | 0x5488bf;
      }
      else {
        uVar9 = *(uint *)(lVar6 + 0x20) & 0x5488bf | uVar9;
      }
    }
    bVar14 = (uVar9 & 0xc08070) != 0;
  }
  if (bVar14) {
    FUN_000e6730(lVar11,local_7b8,0,0xffffffff,0);
  }
  if (0 < *(long *)(param_1 + 0x18)) {
    lVar11 = 0;
    bVar14 = true;
    do {
      lVar6 = *(long *)(param_1 + 0x20);
      plVar3 = (long *)FUN_0025cbd0();
      lVar6 = (**(code **)(*plVar3 + 0x410))
                        (plVar3,*(undefined2 *)(param_1 + 0x20 + lVar11 * 2 + lVar6 + 0x10));
      bVar8 = false;
      if (((lVar6 != 0) && (bVar8 = bVar14, *(long *)(lVar6 + 0x18) != 0)) &&
         (lVar7 = *(long *)(lVar6 + 0x60), lVar7 != 0)) {
        lVar12 = lVar6 + 0x60 + lVar7;
        lVar13 = (long)*(char *)(lVar6 + 0x30 + *(long *)(lVar6 + 0x18));
        lVar7 = FUN_0054c5b0(uVar1,*(undefined2 *)(*(long *)(lVar6 + 0x68 + lVar7) + 0x1a + lVar12))
        ;
        if (lVar7 != 0) {
          FUN_00289d40(0,lVar6,0,0,auStack_790 + lVar13 * 0x40);
          FUN_0054f840(uVar1,param_2,lVar7,*(undefined2 *)(lVar12 + 0x60),0,0,0,
                       local_2b8 + lVar13 * 0x20);
        }
      }
      lVar11 = lVar11 + 1;
      bVar14 = bVar8;
    } while (lVar11 < *(long *)(param_1 + 0x18));
    uVar1 = 0;
    if (!bVar8) goto LAB_0057956f;
  }
  local_954 = 0x811c9dc5;
  local_934 = 0x811c9dc5;
  local_914 = 0x811c9dc5;
  local_8f4 = 0x811c9dc5;
  local_8d4 = 0x811c9dc5;
  local_8b4 = 0x811c9dc5;
  local_894 = 0x811c9dc5;
  local_874 = 0x811c9dc5;
  local_854 = 0x811c9dc5;
  local_834 = 0x811c9dc5;
  local_814 = 0x811c9dc5;
  local_7f4 = 0x811c9dc5;
  local_7d4 = 0x811c9dc5;
  lVar11 = *(long *)(PTR_DAT_019b1b78 + 8);
  uVar1 = FUN_000e8680(lVar11,0,0xffffffff);
  thunk_FUN_012aa986(local_958,0,uVar1);
  uVar10 = *(ushort *)(lVar11 + 0x1c) & 0x78;
  bVar14 = uVar10 != 0;
  if (uVar10 == 0) {
    uVar9 = *(uint *)(lVar11 + 0x20);
    if ((*(ushort *)(lVar11 + 0x1c) & 0x40) != 0) {
      lVar6 = FUN_000e8a90(lVar11,local_958);
      if (lVar6 == 0) {
        uVar9 = uVar9 | 0x5488bf;
      }
      else {
        uVar9 = *(uint *)(lVar6 + 0x20) & 0x5488bf | uVar9;
      }
    }
    bVar14 = (uVar9 & 0xc08070) != 0;
  }
  if (bVar14) {
    FUN_000e6730(lVar11,local_958,0,0xffffffff,0);
  }
  FUN_0090ff40(local_7b8 + (long)*(char *)(lVar2 + 0xb) * 0x40,
               local_2b8 + (long)*(char *)(lVar2 + 0xb) * 0x20,local_958);
  FUN_0090ff40(local_7b8 + (long)*(char *)(lVar2 + 0xc) * 0x40,
               local_2b8 + (long)*(char *)(lVar2 + 0xc) * 0x20,local_938);
  FUN_0090ff40(local_7b8 + (long)*(char *)(lVar2 + 0xd) * 0x40,
               local_2b8 + (long)*(char *)(lVar2 + 0xd) * 0x20,local_918);
  FUN_0090ff40(local_7b8 + (long)*(char *)(lVar2 + 0xe) * 0x40,
               local_2b8 + (long)*(char *)(lVar2 + 0xe) * 0x20,local_8f8);
  FUN_0090ff40(local_7b8 + (long)*(char *)(lVar2 + 0xf) * 0x40,
               local_2b8 + (long)*(char *)(lVar2 + 0xf) * 0x20,local_8d8);
  FUN_0090fef0(uVar4,param_2,local_bb8);
  local_a68 = 0x811c9dc5;
  local_a48 = 0x811c9dc5;
  local_a28 = 0x811c9dc5;
  local_a08 = 0x811c9dc5;
  local_9e8 = 0x811c9dc5;
  local_9c8 = 0x811c9dc5;
  local_9a8 = 0x811c9dc5;
  local_988 = 0x811c9dc5;
  local_980 = 0;
  local_97c = 0x811c9dc5;
  local_978 = 0x811c9dc5;
  local_974 = 0x811c9dc5;
  local_970 = 0x811c9dc5;
  local_96c = 0x811c9dc5;
  local_968 = 0x811c9dc5;
  local_964 = 0x811c9dc5;
  local_960 = 0x811c9dc5;
  FUN_0066b220(local_958,0,0,1,4,0xffffffff,local_a80);
  local_ae4 = 0;
  local_ae0 = 0x811c9dc5;
  local_adc = 0x811c9dc5;
  local_ad8 = 0x811c9dc5;
  local_ad4 = 0x811c9dc5;
  local_ad0 = 0x811c9dc5;
  local_acc = 0x811c9dc5;
  local_ac8 = 0x811c9dc5;
  local_ac4 = 0x811c9dc5;
  local_ac0 = 0x811c9dc5;
  local_ab8 = 0x811c9dc5;
  local_ab0 = 0x811c9dc5;
  local_aa8 = 0x811c9dc5;
  local_aa0 = 0x811c9dc5;
  local_a98 = 0x811c9dc5;
  local_a90 = 0x811c9dc5;
  local_a88 = 0x811c9dc5;
  FUN_00641ad0(local_a80,local_bb0);
  thunk_FUN_012aa7c6(param_3,local_bb0,0xcc);
  uVar1 = 1;
LAB_0057956f:
  if (*DAT_01a1f100 != local_38) {
    uVar1 = thunk_FUN_012aa7f6();
    return uVar1;
  }
  return uVar1;
}

