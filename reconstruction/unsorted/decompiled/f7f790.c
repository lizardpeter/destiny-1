
void FUN_00f7f790(long param_1,undefined4 param_2)

{
  char cVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar2) >> 2) < 2) {
    cVar1 = (**(code **)(param_1 + 0x18))(param_1,2,*(undefined8 *)(param_1 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    puVar2 = *(undefined4 **)(param_1 + 0x10);
  }
  *puVar2 = 0xc0002a00;
  puVar2[1] = param_2;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 8;
  return;
}

