
ulong FUN_0055aa80(int param_1,undefined4 param_2,undefined8 *param_3,undefined8 param_4,
                  undefined4 param_5,undefined8 param_6)

{
  long *plVar1;
  ulong uVar2;
  bool bVar3;
  long lVar4;
  undefined8 *puVar5;
  undefined8 *puVar6;
  bool bVar7;
  byte bVar8;
  undefined8 local_c0;
  undefined8 uStack_b8;
  undefined8 uStack_b0;
  undefined8 uStack_a8;
  undefined8 local_a0;
  undefined8 uStack_98;
  undefined8 uStack_90;
  undefined8 uStack_88;
  undefined8 local_80;
  undefined8 local_78;
  undefined8 local_70;
  long local_60;
  
  bVar8 = 0;
  local_60 = *DAT_01a1f100;
  if (*(int *)(DAT_026b9968 + 8 + (long)param_1 * 0x18) == -1) {
    uVar2 = 0;
  }
  else {
    uVar2 = DAT_026b9968 + 8 + (long)param_1 * 0x18;
  }
  plVar1 = (long *)0x0;
  bVar7 = uVar2 != 0;
  if (bVar7) {
    plVar1 = (long *)FUN_0056a830(*(undefined4 *)(uVar2 + 8));
    uVar2 = (**(code **)(*plVar1 + 0x40))(plVar1);
    bVar3 = false;
    if ((char)uVar2 != '\0') goto LAB_0055ab0c;
  }
  bVar3 = bVar7;
LAB_0055ab0c:
  uVar2 = uVar2 & 0xffffffffffffff00;
  if (bVar3) {
    local_a0 = 0;
    uStack_98 = 0;
    uStack_90 = 0;
    uStack_88 = 0;
    local_c0 = 0;
    uStack_b8 = 0;
    uStack_b0 = 0;
    uStack_a8 = 0;
    local_78 = 0;
    local_80 = 0;
    puVar5 = param_3;
    puVar6 = &local_c0;
    local_70 = param_6;
    for (lVar4 = 9; lVar4 != 0; lVar4 = lVar4 + -1) {
      *puVar6 = *puVar5;
      puVar5 = puVar5 + (ulong)bVar8 * -2 + 1;
      puVar6 = puVar6 + (ulong)bVar8 * -2 + 1;
    }
    local_78 = CONCAT62(local_78._2_6_,*(undefined2 *)(param_3 + 9));
    uVar2 = FUN_00567540(plVar1,param_2,&local_c0,param_4,param_5);
  }
  if (*DAT_01a1f100 == local_60) {
    return uVar2;
  }
  uVar2 = thunk_FUN_012aa7f6();
  return uVar2;
}

