
undefined8 FUN_0029b580(long *param_1)

{
  char cVar1;
  char cVar2;
  char cVar3;
  undefined4 uVar4;
  int iVar5;
  undefined4 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined1 uVar9;
  undefined *puVar10;
  undefined *puVar11;
  undefined8 in_stack_fffffffffffffe68;
  undefined4 *puVar12;
  undefined8 local_180;
  undefined4 local_178 [80];
  long local_38;
  
  uVar4 = (undefined4)((ulong)in_stack_fffffffffffffe68 >> 0x20);
  local_38 = *DAT_01a1f100;
  cVar1 = (**(code **)(*param_1 + 0x18))();
  if (cVar1 != '\0') {
    uVar7 = (**(code **)(*param_1 + 0x10))(param_1);
    local_180 = 0;
    uVar4 = FUN_00057e60(param_1 + 0x1ce);
    local_180 = CONCAT44(local_180._4_4_,uVar4);
    uVar8 = FUN_003430b0();
    uVar4 = FUN_00345620(uVar8);
    puVar12 = local_178;
    local_180 = CONCAT44(uVar4,(undefined4)local_180);
    local_178[0] = 0;
    cVar1 = FUN_00299d10(param_1,uVar7,0x11,*(undefined4 *)PTR_DAT_0191a428,&local_180,8,puVar12);
    uVar4 = (undefined4)((ulong)puVar12 >> 0x20);
    uVar9 = 1;
    if (cVar1 != '\0') goto LAB_0029b721;
  }
  if (DAT_026554b8 == '\0') {
    iVar5 = thunk_FUN_012aa7d6(&DAT_026554b8);
    if (iVar5 != 0) {
      DAT_026554b0 = FUN_000e4a10(s_networking_activity_client___AC___0162227c);
      thunk_FUN_012aa7e6(&DAT_026554b8);
    }
  }
  cVar1 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
  cVar2 = (**(code **)(*param_1 + 0x18))(param_1);
  cVar3 = (**(code **)(*param_1 + 0x18))(param_1);
  puVar10 = &DAT_01621de5;
  puVar11 = &DAT_01621de5;
  if (cVar1 != '\0') {
    puVar11 = &DAT_01621de3;
  }
  if (cVar2 != '\0') {
    puVar10 = &DAT_01621de3;
  }
  if (cVar3 == '\0') {
    uVar7 = FUN_00001df0();
  }
  else {
    uVar7 = (**(code **)(*param_1 + 0x10))(param_1);
  }
  uVar6 = FUN_00057e60(param_1 + 0x1ce);
  uVar9 = 0;
  FUN_01008290(local_178,s_networking_activity_client___AC___0162227c,param_1 + 4,puVar11,puVar10,
               uVar7,CONCAT44(uVar4,uVar6));
  FUN_000e4aa0(DAT_026554b0,local_178);
LAB_0029b721:
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uVar9);
  }
  uVar7 = thunk_FUN_012aa7f6();
  return uVar7;
}

