
undefined8
FUN_0029a0d0(long *param_1,int param_2,undefined1 *param_3,long param_4,undefined8 param_5,
            undefined8 *param_6)

{
  undefined1 uVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  int iVar6;
  undefined4 uVar7;
  undefined8 *puVar8;
  long lVar9;
  undefined8 uVar10;
  undefined *puVar11;
  undefined *puVar12;
  undefined4 *puVar13;
  undefined4 uVar14;
  undefined4 local_c58 [2];
  undefined1 local_c50 [320];
  undefined1 local_b10 [256];
  undefined4 local_a10;
  uint uStack_a0c;
  undefined1 local_a08;
  undefined1 local_a04;
  undefined3 uStack_a03;
  undefined2 uStack_a02;
  undefined1 local_a00;
  undefined3 uStack_9ff;
  undefined2 uStack_9fe;
  undefined4 local_9fc;
  undefined2 auStack_9f8 [64];
  undefined1 local_978 [256];
  undefined1 local_878 [256];
  undefined1 local_778;
  undefined4 local_378 [202];
  undefined8 local_50;
  undefined8 local_48;
  undefined4 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_9fc = 0;
  local_378[0] = 0;
  puVar8 = (undefined8 *)FUN_00068570();
  thunk_FUN_012aa986(&local_a10,0,0x9d8);
  uVar1 = FUN_0003b180();
  local_a10 = CONCAT31(local_a10._1_3_,uVar1);
  if (DAT_026553a8 == '\0') {
    iVar6 = FUN_000694d0();
  }
  else {
    iVar6 = (int)DAT_026553b0;
  }
  uStack_a0c = iVar6 * 0x19660d + 0x3c6ef35fU >> 0x10;
  local_b10[0] = 0;
  if (param_2 == 1) {
    FUN_010080a0(local_b10,&DAT_0160ec9c,*(undefined4 *)(param_4 + 0x104));
  }
  _local_a04 = CONCAT31(uStack_a03,*param_3);
  _local_a04 = CONCAT22(*(undefined2 *)(param_3 + 2),_local_a04);
  lVar9 = 0;
  _local_a00 = CONCAT31(uStack_9ff,param_3[4]);
  _local_a00 = CONCAT22(*(undefined2 *)(param_3 + 6),_local_a00);
  local_9fc = *(undefined4 *)(param_3 + 8);
  do {
    auStack_9f8[lVar9 * 2] = *(undefined2 *)(param_3 + lVar9 * 4 + 0xc);
    auStack_9f8[lVar9 * 2 + 1] = *(undefined2 *)(param_3 + lVar9 * 4 + 0xe);
    lVar9 = lVar9 + 1;
  } while (lVar9 != 0x20);
  local_a08 = (char)param_2;
  FUN_00065030(local_978,param_4,0x100);
  thunk_FUN_012aa7c6(local_878,local_b10,0x100);
  local_48 = *param_6;
  thunk_FUN_012aa7c6(local_378,param_5,0x328);
  local_50 = *puVar8;
  local_40 = FUN_001db3f0();
  local_778 = 0;
  uVar10 = FUN_00001df0();
  puVar13 = local_c58;
  local_c58[0] = 1;
  cVar2 = FUN_00299d10(param_1,uVar10,8,0xffffffff,&local_a10,0x9d8,puVar13);
  uVar14 = (undefined4)((ulong)puVar13 >> 0x20);
  if (cVar2 == '\0') {
    if (DAT_02655438 == '\0') {
      iVar6 = thunk_FUN_012aa7d6(&DAT_02655438);
      if (iVar6 != 0) {
        DAT_02655430 = FUN_000e4a10(s_networking_activity_client___AC___01621e66);
        thunk_FUN_012aa7e6(&DAT_02655438);
      }
    }
    cVar3 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
    cVar4 = (**(code **)(*param_1 + 0x18))(param_1);
    cVar5 = (**(code **)(*param_1 + 0x18))(param_1);
    puVar12 = &DAT_01621de5;
    puVar11 = &DAT_01621de5;
    if (cVar3 != '\0') {
      puVar11 = &DAT_01621de3;
    }
    if (cVar4 != '\0') {
      puVar12 = &DAT_01621de3;
    }
    if (cVar5 == '\0') {
      uVar10 = FUN_00001df0();
    }
    else {
      uVar10 = (**(code **)(*param_1 + 0x10))(param_1);
    }
    uVar7 = FUN_00057e60(param_1 + 0x1ce);
    FUN_01008290(local_c50,s_networking_activity_client___AC___01621e66,param_1 + 4,puVar11,puVar12,
                 uVar10,CONCAT44(uVar14,uVar7));
    FUN_000e4aa0(DAT_02655430,local_c50);
  }
  else {
    *(undefined1 *)(param_1 + 0x28) = local_a08;
    param_1[0x27] = CONCAT44(uStack_a0c,local_a10);
    *(char *)((long)param_1 + 0x144) = (char)_local_a04;
    *(short *)((long)param_1 + 0x146) = (short)((uint)_local_a04 >> 0x10);
    lVar9 = 0;
    *(char *)(param_1 + 0x29) = (char)_local_a00;
    *(short *)((long)param_1 + 0x14a) = (short)((uint)_local_a00 >> 0x10);
    *(undefined4 *)((long)param_1 + 0x14c) = local_9fc;
    do {
      *(undefined2 *)((long)param_1 + lVar9 * 4 + 0x150) = auStack_9f8[lVar9 * 2];
      *(undefined2 *)((long)param_1 + lVar9 * 4 + 0x152) = auStack_9f8[lVar9 * 2 + 1];
      lVar9 = lVar9 + 1;
    } while (lVar9 != 0x20);
    thunk_FUN_012aa7c6(param_1 + 0x3a,local_978,0x93c);
    *(byte *)(param_1 + 0x26) = *(byte *)(param_1 + 0x26) | 2;
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),cVar2);
  }
  uVar10 = thunk_FUN_012aa7f6();
  return uVar10;
}

