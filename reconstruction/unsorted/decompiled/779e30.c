
void FUN_00779e30(long param_1,uint param_2)

{
  undefined8 *puVar1;
  char cVar2;
  int iVar3;
  long lVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined4 *puVar7;
  undefined4 local_478 [2];
  undefined4 local_470 [2];
  undefined8 local_468;
  undefined1 local_460 [256];
  undefined1 local_360 [256];
  undefined1 local_260 [320];
  undefined8 local_120;
  undefined8 uStack_118;
  undefined8 uStack_110;
  undefined8 uStack_108;
  undefined8 local_100;
  undefined8 uStack_f8;
  undefined8 uStack_f0;
  undefined8 uStack_e8;
  undefined8 local_e0;
  undefined4 local_d8;
  undefined2 local_d4;
  undefined8 local_c0;
  undefined8 uStack_b8;
  undefined8 uStack_b0;
  undefined8 uStack_a8;
  undefined8 local_a0;
  undefined8 uStack_98;
  undefined8 uStack_90;
  undefined8 uStack_88;
  undefined8 local_80;
  undefined4 local_78;
  undefined2 local_74;
  long local_60;
  
  local_60 = *DAT_01a1f100;
  if (param_2 == 0) {
    lVar4 = FUN_00775180(2);
  }
  else {
    lVar4 = FUN_00772ec0();
  }
  local_468 = FUN_00001df0();
  local_a0 = 0;
  uStack_98 = 0;
  uStack_90 = 0;
  uStack_88 = 0;
  local_c0 = 0;
  uStack_b8 = 0;
  uStack_b0 = 0;
  uStack_a8 = 0;
  local_74 = 0;
  local_78 = 0;
  local_80 = 0;
  local_100 = 0;
  uStack_f8 = 0;
  uStack_f0 = 0;
  uStack_e8 = 0;
  local_120 = 0;
  uStack_118 = 0;
  uStack_110 = 0;
  uStack_108 = 0;
  puVar7 = (undefined4 *)(param_1 + 0x130);
  if (param_2 == 0) {
    puVar7 = (undefined4 *)(param_1 + 0x90);
  }
  local_d4 = 0;
  local_d8 = 0;
  local_e0 = 0;
  FUN_002e94f0(puVar7 + 5,&local_c0);
  if (*(char *)((long)puVar7 + 0x11) != '\0') {
    local_468 = FUN_0075edd0(1,param_2 != 0);
    if ((*(uint *)(lVar4 + 0x8c48) < 0xb) &&
       ((0x7f0U >> (*(uint *)(lVar4 + 0x8c48) & 0x1f) & 1) != 0)) {
      FUN_00b74250(lVar4,&local_120);
    }
  }
  iVar3 = thunk_FUN_012aa826(&local_120,&local_c0,0x4e);
  if (iVar3 != 0) {
    cVar2 = FUN_000e4d70(4,0);
    if (cVar2 != '\0') {
      if (DAT_026cad20 == '\0') {
        iVar3 = thunk_FUN_012aa7d6(&DAT_026cad20);
        if (iVar3 != 0) {
          DAT_026cad18 = FUN_000e4a10(s_world_controller_slice_set_trans_01651725);
          thunk_FUN_012aa7e6(&DAT_026cad20);
        }
      }
      uVar5 = FUN_00342a30(puVar7);
      uVar6 = FUN_003430b0();
      FUN_00344990(local_470,uVar6,*puVar7);
      FUN_010156f0(local_360,s__8s__HASH__0x_08x__0164efff,uVar5,local_470[0]);
      uVar5 = FUN_002ea0f0(&local_c0);
      uVar6 = FUN_002ea0f0(&local_120);
      FUN_01008290(local_260,s_world_controller_slice_set_trans_01651725,local_360,
                   (&PTR_s_CURRENT_019452f0)[param_2],uVar5,uVar6);
      FUN_000e4aa0(DAT_026cad18,local_260);
    }
    FUN_002e9680(puVar7 + 5,&local_120);
  }
  puVar1 = (undefined8 *)(puVar7 + 0x26);
  cVar2 = FUN_002a35c0(puVar1,&local_468);
  if (cVar2 != '\0') {
    cVar2 = FUN_000e4d70(4,0);
    if (cVar2 != '\0') {
      if (DAT_026cad30 == '\0') {
        iVar3 = thunk_FUN_012aa7d6(&DAT_026cad30);
        if (iVar3 != 0) {
          DAT_026cad28 = FUN_000e4a10(s_world_controller_slice_set_trans_01651798);
          thunk_FUN_012aa7e6(&DAT_026cad30);
        }
      }
      uVar5 = FUN_00342a30(puVar7);
      uVar6 = FUN_003430b0();
      FUN_00344990(local_478,uVar6,*puVar7);
      FUN_010156f0(local_460,s__8s__HASH__0x_08x__0164efff,uVar5,local_478[0]);
      uVar5 = FUN_002a35d0(puVar1);
      uVar6 = FUN_002a35d0(&local_468);
      FUN_01008290(local_260,s_world_controller_slice_set_trans_01651798,local_460,
                   (&PTR_s_CURRENT_019452f0)[param_2],uVar5,uVar6);
      FUN_000e4aa0(DAT_026cad28,local_260);
    }
    *puVar1 = local_468;
  }
  if (*DAT_01a1f100 == local_60) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

