
undefined8 FUN_0029a990(long *param_1,undefined8 *param_2)

{
  long *plVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  undefined4 uVar6;
  int iVar7;
  undefined4 uVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined *puVar11;
  undefined *puVar12;
  undefined4 *puVar13;
  undefined4 local_188 [80];
  undefined8 local_48;
  undefined8 uStack_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_48 = 0;
  uStack_40 = 0;
  plVar1 = param_1 + 0x1ce;
  uVar6 = FUN_00078d50(plVar1);
  local_48 = CONCAT44(local_48._4_4_,uVar6);
  uVar6 = FUN_00057e60(plVar1);
  local_48 = CONCAT44(uVar6,(undefined4)local_48);
  uStack_40 = *param_2;
  uVar9 = (**(code **)(*param_1 + 0x10))(param_1);
  puVar13 = local_188;
  local_188[0] = 0;
  cVar2 = FUN_00299d10(param_1,uVar9,0xd,*(undefined4 *)PTR_DAT_0191a378,&local_48,0x10,puVar13);
  uVar6 = (undefined4)((ulong)puVar13 >> 0x20);
  if (cVar2 == '\0') {
    if (DAT_02655458 == '\0') {
      iVar7 = thunk_FUN_012aa7d6(&DAT_02655458);
      if (iVar7 != 0) {
        DAT_02655450 = FUN_000e4a10(s_networking_activity_client___AC___01621f72);
        thunk_FUN_012aa7e6(&DAT_02655458);
      }
    }
    cVar3 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
    cVar4 = (**(code **)(*param_1 + 0x18))(param_1);
    cVar5 = (**(code **)(*param_1 + 0x18))(param_1);
    puVar11 = &DAT_01621de5;
    puVar12 = &DAT_01621de5;
    if (cVar3 != '\0') {
      puVar12 = &DAT_01621de3;
    }
    if (cVar4 != '\0') {
      puVar11 = &DAT_01621de3;
    }
    if (cVar5 == '\0') {
      uVar9 = FUN_00001df0();
    }
    else {
      uVar9 = (**(code **)(*param_1 + 0x10))(param_1);
    }
    uVar8 = FUN_00057e60(plVar1);
    uVar10 = FUN_00068600(param_2);
    FUN_01008290(local_188,s_networking_activity_client___AC___01621f72,param_1 + 4,puVar12,puVar11,
                 uVar9,CONCAT44(uVar6,uVar8),uVar10);
    FUN_000e4aa0(DAT_02655450,local_188);
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),cVar2);
  }
  uVar9 = thunk_FUN_012aa7f6();
  return uVar9;
}

