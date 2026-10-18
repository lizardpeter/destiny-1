
void FUN_0029b9f0(long *param_1,undefined4 param_2)

{
  char cVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  undefined *puVar7;
  undefined *puVar8;
  undefined4 *puVar9;
  undefined4 uVar10;
  undefined4 local_180 [2];
  undefined4 local_178 [80];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_180[0] = param_2;
  uVar6 = (**(code **)(*param_1 + 0x10))();
  puVar9 = local_178;
  local_178[0] = 0;
  cVar1 = FUN_00299d10(param_1,uVar6,0x24,*(undefined4 *)PTR_DAT_0191a420,local_180,4,puVar9);
  uVar10 = (undefined4)((ulong)puVar9 >> 0x20);
  if (cVar1 == '\0') {
    if (DAT_026554e8 == '\0') {
      iVar4 = thunk_FUN_012aa7d6(&DAT_026554e8);
      if (iVar4 != 0) {
        DAT_026554e0 = FUN_000e4a10(s_networking_activity_client___AC___016223ce);
        thunk_FUN_012aa7e6(&DAT_026554e8);
      }
    }
    cVar1 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
    cVar2 = (**(code **)(*param_1 + 0x18))(param_1);
    cVar3 = (**(code **)(*param_1 + 0x18))(param_1);
    puVar8 = &DAT_01621de5;
    puVar7 = &DAT_01621de5;
    if (cVar1 != '\0') {
      puVar7 = &DAT_01621de3;
    }
    if (cVar2 != '\0') {
      puVar8 = &DAT_01621de3;
    }
    if (cVar3 == '\0') {
      uVar6 = FUN_00001df0();
    }
    else {
      uVar6 = (**(code **)(*param_1 + 0x10))(param_1);
    }
    uVar5 = FUN_00057e60(param_1 + 0x1ce);
    FUN_01008290(local_178,s_networking_activity_client___AC___016223ce,param_1 + 4,puVar7,puVar8,
                 uVar6,CONCAT44(uVar10,uVar5),param_2);
    FUN_000e4aa0(DAT_026554e0,local_178);
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

