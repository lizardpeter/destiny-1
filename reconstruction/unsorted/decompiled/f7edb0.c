
void FUN_00f7edb0(long param_1,int param_2,undefined8 *param_3)

{
  undefined8 uVar1;
  long lVar2;
  char cVar3;
  int iVar4;
  undefined4 *puVar5;
  uint uVar6;
  
  uVar6 = 3;
  if (param_3 != (undefined8 *)0x0) {
    iVar4 = FUN_00057e60(param_3);
    uVar6 = 3;
    if (iVar4 != 0) {
      uVar6 = 0x10;
    }
  }
  if (((uint)((ulong)(*(long *)(param_1 + 8) - *(long *)(param_1 + 0x10)) >> 2) < uVar6) &&
     (cVar3 = (**(code **)(param_1 + 0x18))(param_1,uVar6,*(undefined8 *)(param_1 + 0x20)),
     cVar3 == '\0')) {
    return;
  }
  if ((param_3 == (undefined8 *)0x0) || (iVar4 = FUN_00057e60(param_3), iVar4 == 0)) {
    puVar5 = *(undefined4 **)(param_1 + 0x10);
    *puVar5 = 0xc0016900;
    puVar5[1] = param_2 * 0xf + 0x31c;
    puVar5[2] = 0;
    puVar5 = puVar5 + 3;
  }
  else {
    puVar5 = *(undefined4 **)(param_1 + 0x10);
    *puVar5 = 0xc0066900;
    puVar5[1] = param_2 * 0xf + 0x318;
    *(undefined8 *)(puVar5 + 6) = param_3[2];
    uVar1 = *param_3;
    *(undefined8 *)(puVar5 + 4) = param_3[1];
    *(undefined8 *)(puVar5 + 2) = uVar1;
    lVar2 = *(long *)(param_1 + 0x10);
    *(long *)(param_1 + 0x10) = lVar2 + 0x20;
    *(undefined4 *)(lVar2 + 0x20) = 0xc0046900;
    *(int *)(lVar2 + 0x24) = param_2 * 0xf + 799;
    uVar1 = *(undefined8 *)((long)param_3 + 0x1c);
    *(undefined8 *)(lVar2 + 0x30) = *(undefined8 *)((long)param_3 + 0x24);
    *(undefined8 *)(lVar2 + 0x28) = uVar1;
    lVar2 = *(long *)(param_1 + 0x10);
    *(undefined4 *)(lVar2 + 0x18) = 0xc0001000;
    *(undefined4 *)(lVar2 + 0x1c) = *(undefined4 *)(param_3 + 3);
    puVar5 = (undefined4 *)(lVar2 + 0x20);
  }
  *(undefined4 **)(param_1 + 0x10) = puVar5;
  return;
}

