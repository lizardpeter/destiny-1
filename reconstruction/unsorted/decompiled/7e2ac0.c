
void FUN_007e2ac0(long param_1,undefined8 *param_2)

{
  undefined8 uVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  
  uVar1 = param_2[0x11];
  *(undefined8 *)(param_1 + 0x2690) = param_2[0x10];
  *(undefined8 *)(param_1 + 0x2698) = uVar1;
  uVar1 = param_2[8];
  uVar2 = param_2[9];
  uVar3 = param_2[0xb];
  uVar4 = param_2[0xc];
  uVar5 = param_2[0xd];
  uVar6 = param_2[0xe];
  uVar7 = param_2[0xf];
  *(undefined8 *)(param_1 + 0x2660) = param_2[10];
  *(undefined8 *)((long)&PTR_DAT_00002668 + param_1) = uVar3;
  *(undefined8 *)(FUN_00002650 + param_1) = uVar1;
  *(undefined8 *)(param_1 + 0x2658) = uVar2;
  *(undefined8 *)(FUN_00002680 + param_1) = uVar6;
  *(undefined8 *)(param_1 + 0x2688) = uVar7;
  *(undefined8 *)(thunk_FUN_012aa976 + param_1) = uVar4;
  *(undefined8 *)((long)&PTR_DAT_00002678 + param_1) = uVar5;
  uVar1 = *param_2;
  uVar2 = param_2[1];
  uVar3 = param_2[3];
  uVar4 = param_2[4];
  uVar5 = param_2[5];
  uVar6 = param_2[6];
  uVar7 = param_2[7];
  *(undefined8 *)(param_1 + 0x2620) = param_2[2];
  *(undefined8 *)(&DAT_00002628 + param_1) = uVar3;
  *(undefined8 *)(FUN_00002610 + param_1) = uVar1;
  *(undefined8 *)(param_1 + 0x2618) = uVar2;
  *(undefined8 *)(param_1 + 0x2640) = uVar6;
  *(undefined8 *)(&DAT_00002648 + param_1) = uVar7;
  *(undefined8 *)(FUN_00002630 + param_1) = uVar4;
  *(undefined8 *)(param_1 + 0x2638) = uVar5;
  uVar1 = param_2[0x13];
  *(undefined8 *)(param_1 + 0x26a0) = param_2[0x12];
  *(undefined8 *)(param_1 + 0x26a8) = uVar1;
  return;
}

