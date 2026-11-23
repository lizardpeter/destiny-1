
void FUN_00f80340(undefined4 param_1,undefined4 param_2,long param_3,int param_4,undefined4 *param_5
                 ,undefined4 *param_6)

{
  undefined4 uVar1;
  undefined4 uVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 uVar5;
  undefined4 uVar6;
  long lVar7;
  char cVar8;
  undefined4 *puVar9;
  
  puVar9 = *(undefined4 **)(param_3 + 0x10);
  if ((uint)((ulong)(*(long *)(param_3 + 8) - (long)puVar9) >> 2) < 0xc) {
    cVar8 = (**(code **)(param_3 + 0x18))(param_3,0xc,*(undefined8 *)(param_3 + 0x20));
    if (cVar8 == '\0') {
      return;
    }
    puVar9 = *(undefined4 **)(param_3 + 0x10);
  }
  uVar1 = param_6[2];
  uVar2 = param_5[2];
  uVar3 = *param_6;
  uVar4 = param_6[1];
  uVar5 = *param_5;
  uVar6 = param_5[1];
  *puVar9 = 0xc0026900;
  puVar9[1] = param_4 * 2 + 0xb4;
  puVar9[2] = param_1;
  puVar9[3] = param_2;
  lVar7 = *(long *)(param_3 + 0x10);
  *(long *)(param_3 + 0x10) = lVar7 + 0x10;
  *(undefined4 *)(lVar7 + 0x10) = 0xc0066900;
  *(int *)(lVar7 + 0x14) = param_4 * 6 + 0x10f;
  *(undefined4 *)(lVar7 + 0x18) = uVar5;
  *(undefined4 *)(lVar7 + 0x1c) = uVar3;
  *(undefined4 *)(lVar7 + 0x20) = uVar6;
  *(undefined4 *)(lVar7 + 0x24) = uVar4;
  *(undefined4 *)(lVar7 + 0x28) = uVar2;
  *(undefined4 *)(lVar7 + 0x2c) = uVar1;
  *(long *)(param_3 + 0x10) = *(long *)(param_3 + 0x10) + 0x20;
  return;
}

