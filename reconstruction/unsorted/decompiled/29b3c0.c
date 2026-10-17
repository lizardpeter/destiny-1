
undefined8 FUN_0029b3c0(long *param_1,undefined8 param_2)

{
  char cVar1;
  char cVar2;
  char cVar3;
  int iVar4;
  undefined4 uVar5;
  undefined8 uVar6;
  undefined1 uVar7;
  undefined *puVar8;
  undefined *puVar9;
  undefined4 *puVar10;
  undefined4 uVar11;
  undefined4 local_b8c8 [80];
  undefined1 local_b788 [46928];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  cVar1 = (**(code **)(*param_1 + 0x18))();
  uVar7 = 0;
  if (cVar1 != '\0') {
    thunk_FUN_012aa7c6(local_b788,param_2,0xb750);
    uVar6 = (**(code **)(*param_1 + 0x10))(param_1);
    puVar10 = local_b8c8;
    local_b8c8[0] = 0;
    cVar1 = FUN_00299d10(param_1,uVar6,0x25,*(undefined4 *)PTR_DAT_0191a440,local_b788,0xb750,
                         puVar10);
    uVar11 = (undefined4)((ulong)puVar10 >> 0x20);
    uVar7 = 1;
    if (cVar1 == '\0') {
      if (DAT_026554a8 == '\0') {
        iVar4 = thunk_FUN_012aa7d6(&DAT_026554a8);
        if (iVar4 != 0) {
          DAT_026554a0 = FUN_000e4a10(s_networking_activity_client___AC___01622219);
          thunk_FUN_012aa7e6(&DAT_026554a8);
        }
      }
      cVar1 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
      cVar2 = (**(code **)(*param_1 + 0x18))(param_1);
      cVar3 = (**(code **)(*param_1 + 0x18))(param_1);
      puVar8 = &DAT_01621de5;
      puVar9 = &DAT_01621de5;
      if (cVar1 != '\0') {
        puVar9 = &DAT_01621de3;
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
      uVar7 = 0;
      FUN_01008290(local_b8c8,s_networking_activity_client___AC___01622219,param_1 + 4,puVar9,puVar8
                   ,uVar6,CONCAT44(uVar11,uVar5));
      FUN_000e4aa0(DAT_026554a0,local_b8c8);
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar7);
  }
  uVar6 = thunk_FUN_012aa7f6();
  return uVar6;
}

