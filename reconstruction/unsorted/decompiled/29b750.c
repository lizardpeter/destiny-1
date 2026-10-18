
void FUN_0029b750(long *param_1,undefined8 *param_2)

{
  char cVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined4 uVar8;
  undefined *puVar9;
  undefined *puVar10;
  undefined4 *puVar11;
  undefined8 local_180;
  undefined4 local_178 [80];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_180 = *param_2;
  uVar6 = (**(code **)(*param_1 + 0x10))();
  puVar11 = local_178;
  local_178[0] = 0;
  cVar1 = FUN_00299d10(param_1,uVar6,0x23,*(undefined4 *)PTR_DAT_0191a438,&local_180,8,puVar11);
  uVar8 = (undefined4)((ulong)puVar11 >> 0x20);
  if (cVar1 == '\0') {
    if (DAT_026554d8 == '\0') {
      iVar4 = thunk_FUN_012aa7d6(&DAT_026554d8);
      if (iVar4 != 0) {
        DAT_026554d0 = FUN_000e4a10(s_networking_activity_client___AC___01622355);
        thunk_FUN_012aa7e6(&DAT_026554d8);
      }
    }
    cVar1 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
    cVar2 = (**(code **)(*param_1 + 0x18))(param_1);
    cVar3 = (**(code **)(*param_1 + 0x18))(param_1);
    puVar10 = &DAT_01621de5;
    puVar9 = &DAT_01621de5;
    if (cVar1 != '\0') {
      puVar9 = &DAT_01621de3;
    }
    if (cVar2 != '\0') {
      puVar10 = &DAT_01621de3;
    }
    if (cVar3 == '\0') {
      uVar6 = FUN_00001df0();
    }
    else {
      uVar6 = (**(code **)(*param_1 + 0x10))(param_1);
    }
    uVar5 = FUN_00057e60(param_1 + 0x1ce);
    uVar7 = FUN_00068600(param_2);
    FUN_01008290(local_178,s_networking_activity_client___AC___01622355,param_1 + 4,puVar9,puVar10,
                 uVar6,CONCAT44(uVar8,uVar5),uVar7);
    uVar8 = DAT_026554d0;
  }
  else {
    if (DAT_026554c8 == '\0') {
      iVar4 = thunk_FUN_012aa7d6(&DAT_026554c8);
      if (iVar4 != 0) {
        DAT_026554c0 = FUN_000e4a10(s_networking_activity_client___AC___016222e4);
        thunk_FUN_012aa7e6(&DAT_026554c8);
      }
    }
    cVar1 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
    cVar2 = (**(code **)(*param_1 + 0x18))(param_1);
    cVar3 = (**(code **)(*param_1 + 0x18))(param_1);
    puVar10 = &DAT_01621de5;
    puVar9 = &DAT_01621de5;
    if (cVar1 != '\0') {
      puVar9 = &DAT_01621de3;
    }
    if (cVar2 != '\0') {
      puVar10 = &DAT_01621de3;
    }
    if (cVar3 == '\0') {
      uVar6 = FUN_00001df0();
    }
    else {
      uVar6 = (**(code **)(*param_1 + 0x10))(param_1);
    }
    uVar5 = FUN_00057e60(param_1 + 0x1ce);
    uVar7 = FUN_00068600(param_2);
    FUN_01008290(local_178,s_networking_activity_client___AC___016222e4,param_1 + 4,puVar9,puVar10,
                 uVar6,CONCAT44(uVar8,uVar5),uVar7);
    uVar8 = DAT_026554c0;
  }
  FUN_000e4aa0(uVar8,local_178);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

