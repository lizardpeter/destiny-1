
void FUN_00f7eec0(long param_1,undefined8 *param_2)

{
  undefined4 uVar1;
  undefined8 uVar2;
  long lVar3;
  char cVar4;
  int iVar5;
  undefined4 *puVar6;
  uint uVar7;
  
  uVar7 = 6;
  if (param_2 != (undefined8 *)0x0) {
    uVar7 = 0x18;
  }
  if (((uint)((ulong)(*(long *)(param_1 + 8) - *(long *)(param_1 + 0x10)) >> 2) < uVar7) &&
     (cVar4 = (**(code **)(param_1 + 0x18))(param_1,uVar7,*(undefined8 *)(param_1 + 0x20)),
     cVar4 == '\0')) {
    return;
  }
  if ((param_2 == (undefined8 *)0x0) || (iVar5 = FUN_00066dc0(param_2), iVar5 == 0)) {
    puVar6 = *(undefined4 **)(param_1 + 0x10);
    *puVar6 = 0xc0016900;
    puVar6[1] = 0x10;
    puVar6[2] = 0;
    puVar6[3] = 0xc0016900;
    puVar6[4] = 0x11;
    puVar6[5] = 0;
    puVar6 = puVar6 + 6;
  }
  else {
    puVar6 = *(undefined4 **)(param_1 + 0x10);
    *puVar6 = 0xc0086900;
    puVar6[1] = 0x10;
    *(undefined8 *)(puVar6 + 8) = param_2[3];
    *(undefined8 *)(puVar6 + 6) = param_2[2];
    uVar2 = *param_2;
    *(undefined8 *)(puVar6 + 4) = param_2[1];
    *(undefined8 *)(puVar6 + 2) = uVar2;
    uVar1 = *(undefined4 *)((long)param_2 + 0x2c);
    lVar3 = *(long *)(param_1 + 0x10);
    *(undefined4 *)(lVar3 + 0x28) = 0xc0016900;
    *(undefined4 *)(lVar3 + 0x2c) = 0xf;
    *(undefined4 *)(lVar3 + 0x30) = uVar1;
    uVar1 = *(undefined4 *)(param_2 + 4);
    *(undefined4 *)(lVar3 + 0x34) = 0xc0016900;
    *(undefined4 *)(lVar3 + 0x38) = 2;
    *(undefined4 *)(lVar3 + 0x3c) = uVar1;
    uVar1 = *(undefined4 *)((long)param_2 + 0x24);
    *(undefined4 *)(lVar3 + 0x40) = 0xc0016900;
    *(undefined4 *)(lVar3 + 0x44) = 5;
    *(undefined4 *)(lVar3 + 0x48) = uVar1;
    uVar1 = *(undefined4 *)(param_2 + 5);
    *(undefined4 *)(lVar3 + 0x4c) = 0xc0016900;
    *(undefined4 *)(lVar3 + 0x50) = 0x2af;
    *(undefined4 *)(lVar3 + 0x54) = uVar1;
    *(undefined4 *)(lVar3 + 0x58) = 0xc0001000;
    *(undefined4 *)(lVar3 + 0x5c) = *(undefined4 *)(param_2 + 6);
    puVar6 = (undefined4 *)(lVar3 + 0x60);
  }
  *(undefined4 **)(param_1 + 0x10) = puVar6;
  return;
}

