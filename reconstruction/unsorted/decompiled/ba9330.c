
/* WARNING: Type propagation algorithm not settling */

undefined8 FUN_00ba9330(uint *param_1)

{
  char cVar1;
  bool bVar2;
  int iVar3;
  undefined4 uVar4;
  long lVar5;
  long *plVar6;
  long lVar7;
  undefined8 uVar8;
  long lVar9;
  long lVar10;
  uint uVar11;
  uint uVar12;
  bool bVar13;
  undefined1 local_370 [8];
  uint local_368;
  long local_360;
  undefined1 local_358 [8];
  ushort local_350;
  uint local_348 [2];
  undefined8 local_340;
  uint uStack_338;
  undefined4 uStack_334;
  undefined4 uStack_330;
  undefined4 uStack_32c;
  undefined8 uStack_328;
  undefined8 local_320;
  long alStack_318 [27];
  long local_240 [20];
  undefined1 local_1a0 [320];
  long local_60;
  
  local_60 = *DAT_01a1f100;
  bVar13 = false;
  switch(param_1[3]) {
  case 0:
    lVar7 = FUN_00074a30(DAT_0273ea80,*param_1);
    if (lVar7 == 0) {
      cVar1 = FUN_000e4d70(0x10,4);
      bVar13 = false;
      if (cVar1 == '\0') goto LAB_00ba9b81;
      if ((DAT_028a6178 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_028a6178), iVar3 != 0)) {
        DAT_028a6170 = FUN_000e4a10(s_networking_simulation_players_ap_016979f1);
        thunk_FUN_012aa7e6(&DAT_028a6178);
      }
      FUN_01008290(local_1a0,s_networking_simulation_players_ap_016979f1,*param_1);
      uVar4 = DAT_028a6170;
    }
    else if (*(long *)(lVar7 + 0x614) == *(long *)(param_1 + 1)) {
      if ((*(byte *)(lVar7 + 0x610) & 2) == 0) {
        uVar4 = FUN_00074a60(DAT_0273ea80,*param_1);
        FUN_00911c40(uVar4,(char)param_1[4]);
        bVar13 = true;
        goto LAB_00ba9b81;
      }
      cVar1 = FUN_000e4d70(0x10,4);
      bVar13 = false;
      if (cVar1 == '\0') goto LAB_00ba9b81;
      if ((DAT_028a6158 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_028a6158), iVar3 != 0)) {
        DAT_028a6150 = FUN_000e4a10(s_networking_simulation_players_ap_0169794c);
        thunk_FUN_012aa7e6(&DAT_028a6158);
      }
      FUN_01008290(local_1a0,s_networking_simulation_players_ap_0169794c,*param_1);
      uVar4 = DAT_028a6150;
    }
    else {
      cVar1 = FUN_000e4d70(0x10,4);
      bVar13 = false;
      if (cVar1 == '\0') goto LAB_00ba9b81;
      if ((DAT_028a6168 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_028a6168), iVar3 != 0)) {
        DAT_028a6160 = FUN_000e4a10(s_networking_simulation_players_ap_0169799e);
        thunk_FUN_012aa7e6(&DAT_028a6168);
      }
      FUN_01008290(local_1a0,s_networking_simulation_players_ap_0169799e,*param_1);
      uVar4 = DAT_028a6160;
    }
    break;
  case 1:
    lVar7 = FUN_00074a30(DAT_0273ea80,*param_1);
    lVar5 = FUN_00074a30(DAT_0273ea80,param_1[0x3e]);
    if ((lVar5 == 0) && (lVar7 == 0)) {
      cVar1 = FUN_000e4d70(0x10,4);
      bVar13 = false;
      if (cVar1 == '\0') goto LAB_00ba9b81;
      if ((DAT_028a6148 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_028a6148), iVar3 != 0)) {
        DAT_028a6140 = FUN_000e4a10(s_networking_simulation_players_ap_016978eb);
        thunk_FUN_012aa7e6(&DAT_028a6148);
      }
      FUN_01008290(local_1a0,s_networking_simulation_players_ap_016978eb,*param_1,param_1[0x3e]);
      uVar4 = DAT_028a6140;
    }
    else {
      lVar9 = 0;
      lVar10 = 0;
      if (lVar7 != 0) {
        lVar10 = *(long *)(lVar7 + 0x614);
      }
      if (lVar5 != 0) {
        lVar9 = *(long *)(lVar5 + 0x614);
      }
      if ((lVar10 == *(long *)(param_1 + 1)) && (lVar9 == *(long *)(param_1 + 0x3f))) {
        FUN_00912b10(*param_1,param_1[0x3e]);
        bVar13 = true;
        goto LAB_00ba9b81;
      }
      cVar1 = FUN_000e4d70(0x10,4);
      bVar13 = false;
      if (cVar1 == '\0') goto LAB_00ba9b81;
      if ((DAT_028a6138 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_028a6138), iVar3 != 0)) {
        DAT_028a6130 = FUN_000e4a10(s_networking_simulation_players_ap_0169788c);
        thunk_FUN_012aa7e6(&DAT_028a6138);
      }
      FUN_01008290(local_1a0,s_networking_simulation_players_ap_0169788c,*param_1,param_1[0x3e]);
      uVar4 = DAT_028a6130;
    }
    break;
  case 2:
    lVar7 = FUN_00074a30(DAT_0273ea80,*param_1);
    if (lVar7 == 0) {
      cVar1 = FUN_000e4d70(0x10,4);
      bVar13 = false;
      if (cVar1 == '\0') goto LAB_00ba9b81;
      if ((DAT_028a6128 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_028a6128), iVar3 != 0)) {
        DAT_028a6120 = FUN_000e4a10(s_networking_simulation_players_ap_0169782d);
        thunk_FUN_012aa7e6(&DAT_028a6128);
      }
      FUN_01008290(local_1a0,s_networking_simulation_players_ap_0169782d,*param_1);
      uVar4 = DAT_028a6120;
    }
    else {
      if (*(long *)(lVar7 + 0x614) == *(long *)(param_1 + 1)) {
        bVar13 = false;
        if ((*(byte *)(lVar7 + 0x610) & 2) != 0) {
          uVar4 = FUN_00074a60(DAT_0273ea80,*param_1);
          FUN_00913860(uVar4);
          bVar13 = true;
        }
        goto LAB_00ba9b81;
      }
      cVar1 = FUN_000e4d70(0x10,4);
      bVar13 = false;
      if (cVar1 == '\0') goto LAB_00ba9b81;
      if ((DAT_028a6118 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_028a6118), iVar3 != 0)) {
        DAT_028a6110 = FUN_000e4a10(s_networking_simulation_players_ap_016977d7);
        thunk_FUN_012aa7e6(&DAT_028a6118);
      }
      FUN_01008290(local_1a0,s_networking_simulation_players_ap_016977d7,*param_1);
      uVar4 = DAT_028a6110;
    }
    break;
  case 3:
    lVar7 = FUN_00074a30(DAT_0273ea80,*param_1);
    if ((char)param_1[0xe] == '\0') {
      if (param_1[7] == 0) {
        uVar11 = param_1[8];
        if (uVar11 < 4) {
          local_348[0] = 0;
          plVar6 = local_240;
          FUN_00913a60(local_348,plVar6);
          uVar12 = 0;
          do {
            if (((local_348[0] >> (uVar12 & 0x1f) & 1) != 0) &&
               (*(long *)((long)param_1 + 0x11) == *plVar6)) {
              bVar13 = false;
              bVar2 = uVar12 != 0xffffffff && uVar11 < 4;
              if (uVar12 != 0xffffffff && uVar11 < 4) goto LAB_00ba95c2;
              break;
            }
            plVar6 = plVar6 + 1;
            uVar12 = uVar12 + 1;
          } while ((int)uVar12 < 0x14);
        }
        else {
          bVar13 = false;
        }
      }
      else {
        bVar13 = false;
      }
      goto LAB_00ba9b81;
    }
    bVar2 = true;
    uVar12 = 0xffffffff;
LAB_00ba95c2:
    FUN_00074a80(local_358,DAT_0273ea80);
    lVar5 = FUN_00074a90(local_358);
    local_360 = lVar5;
    if (lVar5 != 0) {
      do {
        lVar10 = DAT_02689588;
        local_360 = lVar5;
        if ((uint)local_350 != *param_1) {
          if (*(long *)(param_1 + 1) == *(long *)(lVar5 + 0x614)) {
            bVar13 = false;
            goto LAB_00ba9b81;
          }
          uVar11 = (*(uint *)(lVar5 + 4) & 0x1fff) * DAT_02689590;
          plVar6 = (long *)FUN_00244270(param_1 + 0x2c,param_1 + 1);
          if (*plVar6 == *(long *)((ulong)uVar11 + 0x18 + lVar10)) {
            bVar13 = false;
            goto LAB_00ba9b81;
          }
          cVar1 = FUN_002638b0((ulong)((*(uint *)(lVar5 + 4) & 0x1fff) * DAT_02689590) + 0x20 +
                               DAT_02689588,param_1 + 0x2a);
          if (cVar1 != '\0') {
            bVar13 = false;
            goto LAB_00ba9b81;
          }
        }
        lVar5 = FUN_00074a90(local_358);
        local_360 = lVar5;
      } while (lVar5 != 0);
    }
    if (!bVar2) {
      bVar13 = false;
      goto LAB_00ba9b81;
    }
    if ((char)param_1[0xe] == '\0') {
      FUN_00074a80(local_370,DAT_0273ea80);
      do {
        lVar5 = FUN_00074a90(local_370);
        if (lVar5 == 0) goto LAB_00ba9bd5;
      } while (((*(uint *)(lVar5 + 0x628) != uVar12) || ((local_368 & 0xffff) == *param_1)) ||
              ((*(uint *)(lVar5 + 0x62c) != param_1[7] && (*(uint *)(lVar5 + 0x630) != param_1[8])))
              );
      cVar1 = FUN_000e4d70(0x10,4);
      bVar13 = false;
      if (cVar1 == '\0') goto LAB_00ba9b81;
      if ((DAT_028a60f8 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_028a60f8), iVar3 != 0)) {
        DAT_028a60f0 = FUN_000e4a10(s_networking_simulation_players_ap_016976e3);
        thunk_FUN_012aa7e6(&DAT_028a60f8);
      }
      FUN_01008290(local_1a0,s_networking_simulation_players_ap_016976e3,*param_1,local_368 & 0xffff
                   ,uVar12,param_1[7],param_1[8],*(undefined4 *)(lVar5 + 0x628),
                   *(undefined4 *)(lVar5 + 0x62c),*(undefined4 *)(lVar5 + 0x630));
      uVar4 = DAT_028a60f0;
    }
    else {
LAB_00ba9bd5:
      alStack_318[0x13] = 0;
      alStack_318[0x14] = 0;
      alStack_318[0x15] = 0;
      alStack_318[0x16] = 0;
      alStack_318[0xf] = 0;
      alStack_318[0x10] = 0;
      alStack_318[0x11] = 0;
      alStack_318[0x12] = 0;
      alStack_318[0xb] = 0;
      alStack_318[0xc] = 0;
      alStack_318[0xd] = 0;
      alStack_318[0xe] = 0;
      alStack_318[7] = 0;
      alStack_318[8] = 0;
      alStack_318[9] = 0;
      alStack_318[10] = 0;
      alStack_318[3] = 0;
      alStack_318[4] = 0;
      alStack_318[5] = 0;
      alStack_318[6] = 0;
      local_320 = 0;
      alStack_318[1] = 0;
      alStack_318[2] = 0;
      uStack_334 = 0;
      uStack_330 = 0;
      uStack_32c = 0;
      uStack_328 = 0;
      alStack_318[0x17] = 0;
      local_340._0_2_ = CONCAT11((char)param_1[0xe],1);
      if ((char)param_1[0xe] == '\0') {
        uStack_334 = (undefined4)*(undefined8 *)((long)param_1 + 0x11);
        uStack_330 = (undefined4)((ulong)*(undefined8 *)((long)param_1 + 0x11) >> 0x20);
        local_340._0_3_ = CONCAT12((char)param_1[7],(undefined2)local_340);
        uStack_338 = param_1[8];
        uStack_328 = *(undefined8 *)(param_1 + 10);
        local_320 = *(undefined8 *)(param_1 + 0xc);
      }
      else {
        local_340._0_3_ = CONCAT12(0xff,(undefined2)local_340);
        uStack_338 = 0xffffffff;
      }
      local_340 = (ulong)(uint3)local_340;
      alStack_318[0] = *(long *)(param_1 + 1);
      thunk_FUN_012aa7c6(alStack_318 + 1,param_1 + 0x10,0xb8);
      if (lVar7 == 0) {
        iVar3 = FUN_0090ee70(*param_1,&local_340,*(undefined1 *)((long)param_1 + 0x39));
        bVar13 = iVar3 != -1;
        goto LAB_00ba9b81;
      }
      cVar1 = FUN_002638b0(alStack_318 + 0xe,
                           (ulong)((*(uint *)(lVar7 + 4) & 0x1fff) * DAT_02689590) + 0x20 +
                           DAT_02689588);
      lVar5 = DAT_02689588;
      uVar11 = DAT_02689590 * (*(uint *)(lVar7 + 4) & 0x1fff);
      plVar6 = (long *)FUN_00244270(alStack_318 + 0xf,alStack_318);
      if (((cVar1 != '\0') || (*plVar6 == *(long *)((ulong)uVar11 + 0x18 + lVar5))) ||
         (alStack_318[0] == *(long *)(lVar7 + 0x614))) {
        bVar13 = false;
        if ((*(byte *)(lVar7 + 0x610) & 2) != 0) {
          uVar4 = FUN_00074a60(DAT_0273ea80,*param_1);
          FUN_0090e840(uVar4,&local_340,*(undefined1 *)((long)param_1 + 0x39));
          bVar13 = true;
        }
        goto LAB_00ba9b81;
      }
      cVar1 = FUN_000e4d70(0x10,4);
      bVar13 = false;
      if (cVar1 == '\0') goto LAB_00ba9b81;
      if ((DAT_028a6108 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_028a6108), iVar3 != 0)) {
        DAT_028a6100 = FUN_000e4a10(s_networking_simulation_players_ap_01697776);
        thunk_FUN_012aa7e6(&DAT_028a6108);
      }
      FUN_01008290(local_1a0,s_networking_simulation_players_ap_01697776,*param_1);
      uVar4 = DAT_028a6100;
    }
    break;
  case 4:
    lVar7 = FUN_00074a30(DAT_0273ea80,*param_1);
    if (lVar7 == 0) {
      cVar1 = FUN_000e4d70(0x10,4);
      bVar13 = false;
      if (cVar1 == '\0') goto LAB_00ba9b81;
      if ((DAT_028a60e8 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_028a60e8), iVar3 != 0)) {
        DAT_028a60e0 = FUN_000e4a10(s_networking_simulation_players_ap_0169767d);
        thunk_FUN_012aa7e6(&DAT_028a60e8);
      }
      FUN_01008290(local_1a0,s_networking_simulation_players_ap_0169767d,*param_1);
      uVar4 = DAT_028a60e0;
    }
    else {
      if (*(long *)(lVar7 + 0x614) == *(long *)(param_1 + 1)) {
        uVar4 = FUN_00074a60(DAT_0273ea80,*param_1);
        FUN_009111c0(uVar4,param_1 + 0x10,0);
        bVar13 = true;
        goto LAB_00ba9b81;
      }
      cVar1 = FUN_000e4d70(0x10,4);
      bVar13 = false;
      if (cVar1 == '\0') goto LAB_00ba9b81;
      if ((DAT_028a60d8 == '\0') && (iVar3 = thunk_FUN_012aa7d6(&DAT_028a60d8), iVar3 != 0)) {
        DAT_028a60d0 = FUN_000e4a10(s__networking_simulation_players_a_0169761f + 1);
        thunk_FUN_012aa7e6(&DAT_028a60d8);
      }
      FUN_01008290(local_1a0,s__networking_simulation_players_a_0169761f + 1,*param_1);
      uVar4 = DAT_028a60d0;
    }
    break;
  default:
    bVar13 = false;
    goto LAB_00ba9b81;
  }
  bVar13 = false;
  FUN_000e4aa0(uVar4,local_1a0);
LAB_00ba9b81:
  if (*DAT_01a1f100 == local_60) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),bVar13);
  }
  uVar8 = thunk_FUN_012aa7f6();
  return uVar8;
}

