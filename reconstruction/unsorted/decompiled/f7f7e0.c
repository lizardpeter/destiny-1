
void FUN_00f7f7e0(long param_1,undefined8 param_2)

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
  *puVar2 = 0xc0012600;
  puVar2[1] = (uint)param_2 & 0xfffffffe;
  puVar2[2] = (uint)((ulong)param_2 >> 0x20) & 0xff;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0xc;
  return;
}

