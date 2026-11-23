
void FUN_00f7f260(long param_1,uint param_2)

{
  undefined4 *puVar1;
  char cVar2;
  uint *puVar3;
  
  puVar3 = *(uint **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar3) >> 2) < 5) {
    cVar2 = (**(code **)(param_1 + 0x18))(param_1,5,*(undefined8 *)(param_1 + 0x20));
    if (cVar2 == '\0') {
      return;
    }
    puVar3 = *(uint **)(param_1 + 0x10);
  }
  *puVar3 = *(uint *)(param_1 + 0x28) & 1 | 0xc0012d00;
  puVar3[1] = param_2;
  puVar3[2] = 2;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0xc;
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

