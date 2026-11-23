
undefined8 FUN_0029d440(long *param_1,undefined8 param_2)

{
  char cVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  int iVar5;
  undefined4 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  long lVar9;
  undefined *puVar10;
  undefined *puVar11;
  undefined4 *puVar12;
  undefined4 uVar13;
  undefined8 local_180;
  undefined4 local_178 [80];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar7 = (**(code **)(*param_1 + 0x10))();
  puVar12 = local_178;
  local_178[0] = 0;
  cVar1 = FUN_00299d10(param_1,uVar7,0x16,*(undefined4 *)PTR_DAT_0191a2f8,param_2,0x28,puVar12);
  uVar13 = (undefined4)((ulong)puVar12 >> 0x20);
  if (cVar1 == '\0') {
    if (DAT_02655628 == '\0') {
      iVar5 = thunk_FUN_012aa7d6(&DAT_02655628);
      if (iVar5 != 0) {
        DAT_02655620 = FUN_000e4a10(s_networking_activity_client_send__01622c92);
        thunk_FUN_012aa7e6(&DAT_02655628);
      }
    }
    cVar2 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
    cVar3 = (**(code **)(*param_1 + 0x18))(param_1);
    cVar4 = (**(code **)(*param_1 + 0x18))(param_1);
    puVar11 = &DAT_01621de5;
    puVar10 = &DAT_01621de5;
    if (cVar2 != '\0') {
      puVar10 = &DAT_01621de3;
    }
    if (cVar3 != '\0') {
      puVar11 = &DAT_01621de3;
    }
    if (cVar4 == '\0') {
      uVar7 = FUN_00001df0();
    }
    else {
      uVar7 = (**(code **)(*param_1 + 0x10))(param_1);
    }
    uVar6 = FUN_00057e60(param_1 + 0x1ce);
    local_180 = (**(code **)(*param_1 + 0x10))(param_1);
    uVar8 = FUN_002a35d0(&local_180);
    FUN_01008290(local_178,s_networking_activity_client_send__01622c92,param_1 + 4,puVar10,puVar11,
                 uVar7,CONCAT44(uVar13,uVar6),uVar8);
    FUN_000e4aa0(DAT_02655620,local_178);
  }
  else if (DAT_026553a8 == '\0') {
    lVar9 = FUN_000694d0();
    param_1[0x1c9] = lVar9;
  }
  else {
    param_1[0x1c9] = DAT_026553b0;
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),cVar1);
  }
  uVar7 = thunk_FUN_012aa7f6();
  return uVar7;
}

