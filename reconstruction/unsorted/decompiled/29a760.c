
undefined8 FUN_0029a760(long *param_1,undefined8 *param_2)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  int iVar5;
  undefined4 uVar6;
  long lVar7;
  undefined8 uVar8;
  undefined *puVar9;
  undefined *puVar10;
  undefined4 *puVar11;
  undefined4 uVar12;
  undefined4 local_4a8 [80];
  undefined4 local_368 [2];
  int local_360;
  undefined8 auStack_358 [100];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  thunk_FUN_012aa986(local_368,0,0x330);
  local_368[0] = FUN_00078d50();
  lVar7 = (long)local_360;
  local_360 = local_360 + 1;
  auStack_358[lVar7 * 5 + 4] = param_2[4];
  auStack_358[lVar7 * 5 + 3] = param_2[3];
  auStack_358[lVar7 * 5 + 2] = param_2[2];
  uVar8 = *param_2;
  auStack_358[lVar7 * 5 + 1] = param_2[1];
  auStack_358[lVar7 * 5] = uVar8;
  uVar8 = (**(code **)(*param_1 + 0x10))(param_1);
  puVar11 = local_4a8;
  local_4a8[0] = 0;
  cVar1 = FUN_00299d10(param_1,uVar8,0xc,*(undefined4 *)PTR_DAT_0191a370,local_368,0x330,puVar11);
  uVar12 = (undefined4)((ulong)puVar11 >> 0x20);
  if (cVar1 == '\0') {
    if (DAT_02655448 == '\0') {
      iVar5 = thunk_FUN_012aa7d6(&DAT_02655448);
      if (iVar5 != 0) {
        DAT_02655440 = FUN_000e4a10(s_networking_activity_client_send__01621ec8);
        thunk_FUN_012aa7e6(&DAT_02655448);
      }
    }
    cVar2 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
    cVar3 = (**(code **)(*param_1 + 0x18))(param_1);
    cVar4 = (**(code **)(*param_1 + 0x18))(param_1);
    puVar9 = &DAT_01621de5;
    puVar10 = &DAT_01621de5;
    if (cVar2 != '\0') {
      puVar10 = &DAT_01621de3;
    }
    if (cVar3 != '\0') {
      puVar9 = &DAT_01621de3;
    }
    if (cVar4 == '\0') {
      uVar8 = FUN_00001df0();
    }
    else {
      uVar8 = (**(code **)(*param_1 + 0x10))(param_1);
    }
    uVar6 = FUN_00057e60(param_1 + 0x1ce);
    FUN_01008290(local_4a8,s_networking_activity_client_send__01621ec8,param_1 + 4,puVar10,puVar9,
                 uVar8,CONCAT44(uVar12,uVar6),local_360,param_2[2],param_2[3]);
    FUN_000e4aa0(DAT_02655440,local_4a8);
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),cVar1);
  }
  uVar8 = thunk_FUN_012aa7f6();
  return uVar8;
}

