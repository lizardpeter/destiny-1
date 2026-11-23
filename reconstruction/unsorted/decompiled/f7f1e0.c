
void FUN_00f7f1e0(long param_1,uint param_2)

{
  char cVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar2) >> 2) < 3) {
    cVar1 = (**(code **)(param_1 + 0x18))(param_1,3,*(undefined8 *)(param_1 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    puVar2 = *(undefined4 **)(param_1 + 0x10);
  }
  *puVar2 = 0xc0017900;
  puVar2[1] = 0x242;
  puVar2[2] = param_2 & 0x3f;
  *(undefined4 **)(param_1 + 0x10) = puVar2 + 3;
  return;
}

