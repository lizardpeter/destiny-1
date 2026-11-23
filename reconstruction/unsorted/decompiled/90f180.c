
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

void FUN_0090f180(uint param_1,char param_2,long param_3)

{
  undefined8 *puVar1;
  long lVar2;
  byte *pbVar3;
  long lVar4;
  undefined1 auVar5 [16];
  undefined1 auVar6 [16];
  undefined1 auVar7 [16];
  undefined8 uVar8;
  byte bVar9;
  char cVar10;
  int iVar11;
  undefined8 uVar12;
  long lVar13;
  uint uVar14;
  ushort uVar15;
  long *plVar16;
  long lVar17;
  uint uVar18;
  long lVar19;
  bool bVar20;
  undefined4 uVar21;
  uint local_68 [2];
  long local_60;
  undefined1 local_58 [8];
  uint local_50;
  long local_48;
  long local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar17 = *(long *)(DAT_0273ea80 + 8);
  uVar14 = 0xffffffff;
  if (*(char *)(param_3 + 1) == '\0') {
    uVar18 = 0;
    plVar16 = DAT_0273ea90;
    do {
      plVar16 = plVar16 + 1;
      if (((*(uint *)((long)DAT_0273ea90 + 4) >> (uVar18 & 0x1f) & 1) != 0) &&
         (uVar14 = uVar18, *(long *)(param_3 + 0xc) == *plVar16)) break;
      uVar18 = uVar18 + 1;
      uVar14 = 0xffffffff;
    } while ((int)uVar18 < 0x14);
  }
  lVar19 = (ulong)(param_1 & 0xffff) * 0x2af0;
  *(undefined4 *)(lVar17 + 0x694 + lVar19) = 0xffffffff;
  *(undefined2 *)(lVar17 + 0x698 + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x690 + lVar19) = 0xffffffff;
  *(undefined8 *)(lVar17 + 0x688 + lVar19) = 0xffffffffffffffff;
  *(undefined8 *)(lVar17 + 0x680 + lVar19) = 0xffffffffffffffff;
  *(undefined8 *)(lVar17 + 0x678 + lVar19) = 0xffffffffffffffff;
  bVar9 = *(byte *)(lVar17 + 0x14 + lVar19);
  if (param_2 == '\0') {
    bVar9 = bVar9 & 0xfe;
  }
  else {
    bVar9 = bVar9 | 1;
  }
  *(byte *)(lVar17 + 0x14 + lVar19) = bVar9;
  puVar1 = (undefined8 *)(lVar17 + 0x2c + lVar19);
  *(undefined4 *)(puVar1 + 3) = 0;
  puVar1[2] = 0;
  puVar1[1] = 0;
  *puVar1 = 0;
  *(undefined4 *)(lVar17 + 0x3c + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x40 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x34 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x158 + lVar19) = 0xffffffff;
  thunk_FUN_012aa986(lVar17 + 400 + lVar19,0,0x480);
  uVar8 = uRam000000000166b458;
  uVar12 = _DAT_0166b450;
  *(undefined1 *)(lVar17 + 0x184 + lVar19) = 0;
  *(undefined8 *)(lVar17 + 0x17c + lVar19) = 0;
  *(undefined8 *)(lVar17 + 0x174 + lVar19) = 0;
  *(undefined8 *)(lVar17 + 0x16c + lVar19) = 0;
  *(undefined8 *)(lVar17 + 0x164 + lVar19) = 0;
  *(undefined8 *)(lVar17 + 0x15c + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x5b0 + lVar19) = 0xffffffff;
  *(undefined8 *)(lVar17 + 0x5b4 + lVar19) = 0xffffffffffffffff;
  auVar7 = _DAT_01ac62b0;
  puVar1 = (undefined8 *)(lVar17 + 0x5e0 + lVar19);
  *puVar1 = uVar12;
  puVar1[1] = uVar8;
  auVar5 = vandps_avx(auVar7,_DAT_0166b460);
  auVar6._8_8_ = uRam000000000166b458;
  auVar6._0_8_ = _DAT_0166b450;
  auVar6 = vandnps_avx(auVar7,auVar6);
  auVar5 = vorps_avx(auVar6,auVar5);
  *(undefined1 (*) [16])(lVar17 + 0x5f0 + lVar19) = auVar5;
  *(undefined4 *)(lVar17 + 0x600 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x5d0 + lVar19) = 0x811c9dc5;
  *(undefined4 *)(lVar17 + 0x5d8 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x5d4 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x5dc + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x610 + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x61c + lVar19) = 0xffffffff;
  *(undefined8 *)(lVar17 + 0x614 + lVar19) = *(undefined8 *)(param_3 + 0x28);
  *(uint *)(lVar17 + 0x628 + lVar19) = uVar14;
  *(undefined8 *)(lVar17 + 0x620 + lVar19) = *(undefined8 *)(param_3 + 0xc);
  *(int *)(lVar17 + 0x62c + lVar19) = (int)*(char *)(param_3 + 2);
  *(undefined4 *)(lVar17 + 0x630 + lVar19) = *(undefined4 *)(param_3 + 8);
  *(undefined8 *)(lVar17 + 0x638 + lVar19) = *(undefined8 *)(param_3 + 0x18);
  uVar21 = FUN_005284d0();
  *(undefined4 *)(lVar17 + 0x2848 + lVar19) = uVar21;
  *(undefined8 *)(lVar17 + 0x64c + lVar19) = 0xffffffffffffffff;
  *(undefined8 *)(lVar17 + 0x644 + lVar19) = 0xffffffffffffffff;
  *(undefined1 *)(lVar17 + 0x65c + lVar19) = 2;
  puVar1 = (undefined8 *)(lVar17 + 0x660 + lVar19);
  *puVar1 = uVar12;
  puVar1[1] = uVar8;
  *(undefined4 *)(lVar17 + 0x670 + lVar19) = 0x3f800000;
  *(undefined4 *)(lVar17 + 0x81c + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x820 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x818 + lVar19) = 0;
  *(undefined1 *)(lVar17 + 0x2842 + lVar19) = 0;
  if ((char)DAT_0273ea90[0x15] != '\0') {
    local_40 = *(long *)((long)DAT_0273ea90 + 0xa9);
    if (*(long *)(*(long *)(DAT_0273ea80 + 8) + 0x620 + lVar19) == local_40) {
      FUN_0040fbc0(*(long *)(DAT_0273ea80 + 8) + 400 + lVar19,*(undefined4 *)(lVar17 + 4 + lVar19));
    }
  }
  FUN_00629aa0(lVar17 + 0x828 + lVar19);
  *(undefined4 *)(lVar17 + 0x838 + lVar19) = 0;
  lVar4 = *(long *)(PTR_DAT_019b4650 + 8);
  uVar12 = FUN_000e8680(lVar4,0,0xffffffff);
  lVar2 = lVar17 + 0xc + lVar19;
  thunk_FUN_012aa986(lVar2,0,uVar12);
  uVar15 = *(ushort *)(lVar4 + 0x1c) & 0x78;
  bVar20 = uVar15 != 0;
  if (uVar15 == 0) {
    uVar14 = *(uint *)(lVar4 + 0x20);
    if ((*(ushort *)(lVar4 + 0x1c) & 0x40) != 0) {
      lVar13 = FUN_000e8a90(lVar4,lVar2);
      if (lVar13 == 0) {
        uVar14 = uVar14 | 0x5488bf;
      }
      else {
        uVar14 = *(uint *)(lVar13 + 0x20) & 0x5488bf | uVar14;
      }
    }
    bVar20 = (uVar14 & 0xc08070) != 0;
  }
  if (bVar20) {
    FUN_000e6730(lVar4,lVar2,0,0xffffffff,0);
  }
  *(undefined4 *)(lVar17 + 0x83c + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x840 + lVar19) = 0xffffffff;
  *(undefined8 *)(lVar17 + 0x844 + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x84c + lVar19) = 0xffffffff;
  *(undefined1 *)(lVar17 + 0x2838 + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x283c + lVar19) = 0;
  *(undefined1 *)(lVar17 + 0x2840 + lVar19) = 0;
  *(undefined1 *)(lVar17 + 0x2841 + lVar19) = 0;
  *(undefined1 *)(lVar17 + 0x2868 + lVar19) = 1;
  *(undefined4 *)(lVar17 + 0x286c + lVar19) = 3;
  if (param_2 != '\0') {
    *(undefined4 *)(lVar17 + 0x38 + lVar19) = 0;
  }
  *(undefined4 *)(lVar17 + 0x270c + lVar19) = 0xffffffff;
  iVar11 = *(int *)(lVar17 + 0x628 + lVar19);
  if ((iVar11 != -1) && (iVar11 == *(int *)((long)DAT_0273ea90 + 0xb4))) {
    cVar10 = FUN_00906f70();
    if (cVar10 != '\0') {
      FUN_00074a80(local_58,DAT_0273ea80);
LAB_0090f650:
      do {
        local_60 = FUN_00074a90(local_58);
        if (local_60 != 0) {
          if ((*(byte *)(local_60 + 0x610) & 2) != 0) goto LAB_0090f650;
        }
        if (local_60 == 0) {
          if (*(char *)(param_3 + 1) == '\0') {
            FUN_0090e120(1);
          }
          goto LAB_0090f6d0;
        }
        if ((local_50 != param_1) &&
           (*(int *)(local_60 + 0x628) == *(int *)((long)DAT_0273ea90 + 0xb4))) goto LAB_0090f6d0;
      } while( true );
    }
    FUN_00922ef0(param_1,(int)*(char *)(param_3 + 2));
    FUN_00923080(param_1,*(undefined4 *)(param_3 + 8));
    FUN_00923430((int)*(char *)(param_3 + 2),param_1);
  }
LAB_0090f6d0:
  thunk_FUN_012aa986(lVar17 + 0x6a8 + lVar19,0,0xb8);
  *(undefined1 *)(lVar17 + 0x702 + lVar19) = 0xff;
  *(undefined4 *)(lVar17 + 0x738 + lVar19) = 0xffffffff;
  FUN_0066acc0(lVar17 + 0x1660 + lVar19);
  FUN_009111c0(param_1,param_3 + 0x30,1);
  FUN_00302ae0(*(undefined4 *)(lVar17 + 4 + lVar19));
  if (*(char *)(param_3 + 1) != '\0') {
    pbVar3 = (byte *)(lVar17 + 0x610 + lVar19);
    *pbVar3 = *pbVar3 | 2;
    FUN_00302b20(*(undefined4 *)(lVar17 + 4 + lVar19));
    uVar21 = FUN_005916f0();
    *(undefined4 *)(lVar17 + 0x61c + lVar19) = uVar21;
  }
  FUN_0073d590(lVar17 + 0x2930 + lVar19);
  *(undefined8 *)(lVar17 + 0x2700 + lVar19) = 0xffffffffffffffff;
  *(undefined8 *)(lVar17 + 0x26f8 + lVar19) = 0xffffffffffffffff;
  FUN_001d3770(lVar17 + 10000 + lVar19);
  FUN_001d3770(lVar17 + 0x2740 + lVar19);
  FUN_001d3770(lVar17 + 0x2770 + lVar19);
  FUN_001d3770(lVar17 + 0x27a8 + lVar19);
  FUN_001d3770(lVar17 + 0x27f8 + lVar19);
  *(undefined4 *)(lVar17 + 0x2828 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x27a0 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x69c + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x6a0 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x282c + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x2830 + lVar19) = 0xffffffff;
  *(undefined1 *)(lVar17 + 0x676 + lVar19) = 0xff;
  *(undefined8 *)(lVar17 + 0x2708 + lVar19) = 0xffffffffffffffff;
  *(undefined4 *)(lVar17 + 0x27f0 + lVar19) = 0xffffffff;
  *(undefined8 *)(lVar17 + 0x27e8 + lVar19) = 0xffffffffffffffff;
  *(undefined8 *)(lVar17 + 0x27e0 + lVar19) = 0xffffffffffffffff;
  *(undefined8 *)(lVar17 + 0x27d8 + lVar19) = 0xffffffffffffffff;
  *(undefined4 *)(lVar17 + 0x2834 + lVar19) = 0;
  FUN_0054dd80(lVar17 + 0x850 + lVar19);
  puVar1 = (undefined8 *)(lVar17 + 0x2870 + lVar19);
  *(undefined4 *)(lVar17 + 0x2884 + lVar19) = 0x447a0000;
  *(undefined4 *)(lVar17 + 0x2888 + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x288c + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x2890 + lVar19) = 0x3f800000;
  *(undefined4 *)(lVar17 + 0x2894 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x2898 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x289c + lVar19) = 0x447a0000;
  *(undefined4 *)(lVar17 + 0x28a0 + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x28a4 + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x28a8 + lVar19) = 0x3f800000;
  *(undefined4 *)(lVar17 + 0x28ac + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x28b0 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x28b4 + lVar19) = 0x447a0000;
  *(undefined4 *)(lVar17 + 0x28b8 + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x28bc + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x28c0 + lVar19) = 0x3f800000;
  *(undefined4 *)(lVar17 + 0x28c4 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x28c8 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x28cc + lVar19) = 0x447a0000;
  *(undefined4 *)(lVar17 + 0x28d0 + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x28d4 + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x28d8 + lVar19) = 0x3f800000;
  *(undefined4 *)(lVar17 + 0x28dc + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x28e0 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x28e4 + lVar19) = 0x447a0000;
  *(undefined4 *)(lVar17 + 0x28e8 + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x28ec + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x28f0 + lVar19) = 0x3f800000;
  *(undefined4 *)(lVar17 + 0x28f4 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x28f8 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x28fc + lVar19) = 0x447a0000;
  *(undefined4 *)(lVar17 + 0x2900 + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x2904 + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x2908 + lVar19) = 0x3f800000;
  *(undefined8 *)(lVar17 + 0x290c + lVar19) = 0xffffffffffffffff;
  puVar1[1] = 0;
  *puVar1 = 0;
  *(undefined4 *)puVar1 = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x2880 + lVar19) = 0;
  *(undefined4 *)(lVar17 + 0x291c + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x2920 + lVar19) = 0xffffffff;
  *(undefined4 *)(lVar17 + 0x2918 + lVar19) = 0xffffffff;
  *(undefined8 *)(lVar17 + 0x24 + lVar19) = 0x811c9dc5811c9dc5;
  FUN_00254b90(lVar17 + 0x2a10 + lVar19);
  if ((char)DAT_0273ea90[0x15] != '\0') {
    local_48 = *(long *)((long)DAT_0273ea90 + 0xa9);
    if (*(long *)(*(long *)(DAT_0273ea80 + 8) + 0x620 + lVar19) == local_48) {
      FUN_0011a2b0(*(long *)(DAT_0273ea80 + 8) + 0x80 + lVar19);
      auVar6 = _DAT_01ac62b0;
      uVar12 = uRam000000000166b458;
      lVar2 = *(long *)(DAT_0273ea80 + 8);
      puVar1 = (undefined8 *)(lVar2 + 0x60 + lVar19);
      *puVar1 = _DAT_0166b450;
      puVar1[1] = uVar12;
      auVar5 = vandps_avx(auVar6,_DAT_0166b460);
      auVar7._8_8_ = uRam000000000166b458;
      auVar7._0_8_ = _DAT_0166b450;
      auVar6 = vandnps_avx(auVar6,auVar7);
      auVar5 = vorps_avx(auVar6,auVar5);
      *(undefined1 (*) [16])(lVar2 + 0x70 + lVar19) = auVar5;
    }
  }
  FUN_0058ebd0(lVar17 + 0x710 + lVar19);
  local_68[0] = param_1;
  if ((DAT_02f602d8 == '\0') && (iVar11 = thunk_FUN_012aa7d6(&DAT_02f602d8), iVar11 != 0)) {
    DAT_02f601d0 = 0;
    thunk_FUN_012aa7e6(&DAT_02f602d8);
  }
  if (DAT_02f601c8 == '\0') {
    DAT_02f601d0 = 0;
    DAT_02f601c8 = '\x01';
  }
  else if (0 < DAT_02f601d0) {
    lVar17 = 0;
    iVar11 = DAT_02f601d0;
    do {
      if ((code *)(&DAT_02f601d8)[lVar17] != (code *)0x0) {
        (*(code *)(&DAT_02f601d8)[lVar17])(local_68);
        iVar11 = DAT_02f601d0;
      }
      lVar17 = lVar17 + 1;
    } while ((int)lVar17 < iVar11);
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

