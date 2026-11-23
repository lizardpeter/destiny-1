
void FUN_007e2b50(long param_1)

{
  long lVar1;
  undefined8 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  undefined8 uVar5;
  undefined8 uVar6;
  undefined8 uVar7;
  undefined8 uVar8;
  undefined8 *puVar9;
  
  puVar9 = (undefined8 *)FUN_00f7feb0(*(undefined8 *)(param_1 + 0x50),0xa0,4);
  if (puVar9 != (undefined8 *)0x0) {
    uVar2 = *(undefined8 *)(param_1 + 0x2698);
    puVar9[0x10] = *(undefined8 *)(param_1 + 0x2690);
    puVar9[0x11] = uVar2;
    uVar2 = *(undefined8 *)(FUN_00002650 + param_1);
    uVar3 = *(undefined8 *)(param_1 + 0x2658);
    uVar4 = *(undefined8 *)((long)&PTR_DAT_00002668 + param_1);
    uVar5 = *(undefined8 *)(thunk_FUN_012aa976 + param_1);
    uVar6 = *(undefined8 *)((long)&PTR_DAT_00002678 + param_1);
    uVar7 = *(undefined8 *)(FUN_00002680 + param_1);
    uVar8 = *(undefined8 *)(param_1 + 0x2688);
    puVar9[10] = *(undefined8 *)(param_1 + 0x2660);
    puVar9[0xb] = uVar4;
    puVar9[8] = uVar2;
    puVar9[9] = uVar3;
    puVar9[0xe] = uVar7;
    puVar9[0xf] = uVar8;
    puVar9[0xc] = uVar5;
    puVar9[0xd] = uVar6;
    uVar7 = *(undefined8 *)(FUN_00002610 + param_1);
    uVar8 = *(undefined8 *)(param_1 + 0x2618);
    uVar2 = *(undefined8 *)(&DAT_00002628 + param_1);
    uVar3 = *(undefined8 *)(FUN_00002630 + param_1);
    uVar4 = *(undefined8 *)(param_1 + 0x2638);
    uVar5 = *(undefined8 *)(param_1 + 0x2640);
    uVar6 = *(undefined8 *)(&DAT_00002648 + param_1);
    puVar9[2] = *(undefined8 *)(param_1 + 0x2620);
    puVar9[3] = uVar2;
    *puVar9 = uVar7;
    puVar9[1] = uVar8;
    puVar9[6] = uVar5;
    puVar9[7] = uVar6;
    puVar9[4] = uVar3;
    puVar9[5] = uVar4;
    lVar1 = param_1 + 0x25f4;
    uVar2 = *(undefined8 *)(param_1 + 0x26a8);
    puVar9[0x12] = *(undefined8 *)(param_1 + 0x26a0);
    puVar9[0x13] = uVar2;
    FUN_00f7d180(lVar1,puVar9,0xa0);
    FUN_00f7d010(lVar1,0x10);
    FUN_00f8b500(*(long *)(param_1 + 0x50) + 0xc0,2,0,1,lVar1);
    return;
  }
  return;
}

