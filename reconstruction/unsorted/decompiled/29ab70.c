
undefined8 FUN_0029ab70(long *param_1,undefined4 *param_2)

{
  undefined4 uVar1;
  char cVar2;
  char cVar3;
  char cVar4;
  char cVar5;
  int iVar6;
  undefined4 uVar7;
  undefined4 uVar8;
  undefined8 uVar9;
  undefined8 uVar10;
  undefined8 uVar11;
  undefined8 uVar12;
  undefined8 uVar13;
  undefined8 uVar14;
  undefined *puVar15;
  undefined *puVar16;
  undefined4 *puVar17;
  undefined4 uVar19;
  undefined8 uVar18;
  undefined8 in_stack_fffffffffffffe08;
  undefined4 local_178 [80];
  long local_38;
  
  uVar8 = (undefined4)((ulong)in_stack_fffffffffffffe08 >> 0x20);
  local_38 = *DAT_01a1f100;
  local_178[0] = 0;
  puVar17 = local_178;
  cVar2 = FUN_00299d10(param_1,*(undefined8 *)(param_2 + 2),3,*(undefined4 *)PTR_DAT_0191a380,
                       param_2,0x100,puVar17);
  uVar19 = (undefined4)((ulong)puVar17 >> 0x20);
  if (cVar2 == '\0') {
    if (DAT_02655488 == '\0') {
      iVar6 = thunk_FUN_012aa7d6(&DAT_02655488);
      if (iVar6 != 0) {
        DAT_02655480 = FUN_000e4a10(s_networking_activity_client___AC___01622124);
        thunk_FUN_012aa7e6(&DAT_02655488);
      }
    }
    cVar3 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
    cVar4 = (**(code **)(*param_1 + 0x18))(param_1);
    cVar5 = (**(code **)(*param_1 + 0x18))(param_1);
    puVar16 = &DAT_01621de5;
    puVar15 = &DAT_01621de5;
    if (cVar3 != '\0') {
      puVar15 = &DAT_01621de3;
    }
    if (cVar4 != '\0') {
      puVar16 = &DAT_01621de3;
    }
    if (cVar5 == '\0') {
      uVar9 = FUN_00001df0();
    }
    else {
      uVar9 = (**(code **)(*param_1 + 0x10))(param_1);
    }
    uVar8 = FUN_00057e60(param_1 + 0x1ce);
    uVar13 = FUN_002a35d0(param_2 + 2);
    FUN_01008290(local_178,s_networking_activity_client___AC___01622124,param_1 + 4,puVar15,puVar16,
                 uVar9,CONCAT44(uVar19,uVar8),uVar13,*(undefined8 *)(param_2 + 8),
                 *(undefined8 *)(param_2 + 10));
    FUN_000e4aa0(DAT_02655480,local_178);
  }
  else {
    if (DAT_02655468 == '\0') {
      iVar6 = thunk_FUN_012aa7d6(&DAT_02655468);
      if (iVar6 != 0) {
        DAT_02655460 = FUN_000e4a10(s_networking_activity_client___AC___01621fee);
        thunk_FUN_012aa7e6(&DAT_02655468);
      }
    }
    cVar3 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
    cVar4 = (**(code **)(*param_1 + 0x18))(param_1);
    cVar5 = (**(code **)(*param_1 + 0x18))(param_1);
    puVar15 = &DAT_01621de5;
    if (cVar3 != '\0') {
      puVar15 = &DAT_01621de3;
    }
    puVar16 = &DAT_01621de5;
    if (cVar4 != '\0') {
      puVar16 = &DAT_01621de3;
    }
    if (cVar5 == '\0') {
      uVar9 = FUN_00001df0();
    }
    else {
      uVar9 = (**(code **)(*param_1 + 0x10))(param_1);
    }
    uVar7 = FUN_00057e60();
    uVar10 = FUN_002a35d0(param_2 + 2);
    uVar1 = *param_2;
    uVar13 = *(undefined8 *)(param_2 + 8);
    uVar14 = *(undefined8 *)(param_2 + 10);
    uVar11 = FUN_00068600(param_2 + 4);
    uVar12 = FUN_002487e0(param_2 + 6);
    uVar18 = CONCAT44(uVar19,uVar7);
    FUN_01008290(local_178,s_networking_activity_client___AC___01621fee,param_1 + 4,puVar15,puVar16,
                 uVar9,uVar18,uVar10,CONCAT44(uVar8,uVar1),uVar13,uVar14,uVar11,uVar12);
    uVar19 = (undefined4)((ulong)uVar18 >> 0x20);
    FUN_000e4aa0(DAT_02655460,local_178);
    if (DAT_02655478 == '\0') {
      iVar6 = thunk_FUN_012aa7d6(&DAT_02655478);
      if (iVar6 != 0) {
        DAT_02655470 = FUN_000e4a10(s_networking_activity_client___AC___0162209f);
        thunk_FUN_012aa7e6(&DAT_02655478);
      }
    }
    cVar3 = (**(code **)(*(long *)param_1[0x1ca] + 0x18))();
    cVar4 = (**(code **)(*param_1 + 0x18))(param_1);
    cVar5 = (**(code **)(*param_1 + 0x18))(param_1);
    puVar15 = &DAT_01621de5;
    puVar16 = &DAT_01621de5;
    if (cVar3 != '\0') {
      puVar16 = &DAT_01621de3;
    }
    if (cVar4 != '\0') {
      puVar15 = &DAT_01621de3;
    }
    if (cVar5 == '\0') {
      uVar9 = FUN_00001df0();
    }
    else {
      uVar9 = (**(code **)(*param_1 + 0x10))(param_1);
    }
    uVar8 = FUN_00057e60(param_1 + 0x1ce);
    uVar13 = FUN_002a35d0(param_2 + 0x32);
    uVar14 = FUN_002a35d0(param_2 + 0x34);
    FUN_01008290(local_178,s_networking_activity_client___AC___0162209f,param_1 + 4,puVar16,puVar15,
                 uVar9,CONCAT44(uVar19,uVar8),(long)param_2 + 0x39,uVar13,uVar14,
                 *(undefined8 *)(param_2 + 0x36));
    FUN_000e4aa0(DAT_02655470,local_178);
    thunk_FUN_012aa7c6(param_1 + 0x173,param_2,0x100);
    *(byte *)(param_1 + 0x26) = *(byte *)(param_1 + 0x26) | 8;
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),cVar2);
  }
  uVar9 = thunk_FUN_012aa7f6();
  return uVar9;
}

