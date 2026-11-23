
void FUN_00f81220(long param_1)

{
  char cVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar2) >> 2) < 0x40) {
    cVar1 = (**(code **)(param_1 + 0x18))(param_1,0x40,*(undefined8 *)(param_1 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    puVar2 = *(undefined4 **)(param_1 + 0x10);
  }
  *puVar2 = 0xc03e1000;
  puVar2[1] = 0x68750777;
  *(undefined4 **)(param_1 + 0x10) = puVar2 + 0x40;
  return;
}

