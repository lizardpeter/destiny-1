
void FUN_00f7f320(long param_1,uint param_2,undefined8 param_3)

{
  undefined4 *puVar1;
  char cVar2;
  uint *puVar3;
  
  puVar3 = *(uint **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar3) >> 2) < 8) {
    cVar2 = (**(code **)(param_1 + 0x18))(param_1,8,*(undefined8 *)(param_1 + 0x20));
    if (cVar2 == '\0') {
      return;
    }
    puVar3 = *(uint **)(param_1 + 0x10);
  }
  *puVar3 = *(uint *)(param_1 + 0x28) & 1 | 0xc0042700;
  puVar3[1] = param_2;
  puVar3[2] = (uint)param_3 & 0xfffffffe;
  puVar3[3] = (uint)((ulong)param_3 >> 0x20);
  puVar3[4] = param_2;
  puVar3[5] = 0;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0x18;
  cVar2 = FUN_00f848f0();
  if (cVar2 == '\0') {
    puVar1 = *(undefined4 **)(param_1 + 0x10);
    *puVar1 = 0xc0001000;
    puVar1[1] = 0;
    *(undefined4 **)(param_1 + 0x10) = puVar1 + 2;
  }
  else {
    puVar3 = *(uint **)(param_1 + 0x10);
    *puVar3 = *(uint *)(param_1 + 0x28) & 2 | 0xc0004600;
    puVar3[1] = 0x35;
    *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 8;
  }
  return;
}

