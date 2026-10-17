
void FUN_00f7f4a0(long param_1,uint param_2,uint param_3,uint param_4)

{
  char cVar1;
  uint *puVar2;
  undefined4 *puVar3;
  
  puVar2 = *(uint **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar2) >> 2) < 7) {
    cVar1 = (**(code **)(param_1 + 0x18))(param_1,7,*(undefined8 *)(param_1 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    puVar2 = *(uint **)(param_1 + 0x10);
  }
  *puVar2 = *(uint *)(param_1 + 0x28) & 1 | 0xc0031502;
  puVar2[1] = param_2;
  puVar2[2] = param_3;
  puVar2[3] = param_4;
  puVar2[4] = 1;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0x14;
  cVar1 = FUN_00f848f0();
  if (cVar1 == '\0') {
    puVar3 = *(undefined4 **)(param_1 + 0x10);
    *puVar3 = 0xc0001000;
    puVar3[1] = 0;
  }
  else {
    puVar2 = *(uint **)(param_1 + 0x10);
    *puVar2 = *(uint *)(param_1 + 0x28) & 2 | 0xc0004600;
    puVar2[1] = 0x35;
    puVar3 = *(undefined4 **)(param_1 + 0x10);
  }
  *(undefined4 **)(param_1 + 0x10) = puVar3 + 2;
  return;
}

