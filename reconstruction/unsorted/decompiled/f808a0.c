
void FUN_00f808a0(undefined4 param_1,undefined4 param_2,long param_3)

{
  char cVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(param_3 + 0x10);
  if ((uint)((ulong)(*(long *)(param_3 + 8) - (long)puVar2) >> 2) < 4) {
    cVar1 = (**(code **)(param_3 + 0x18))(param_3,4,*(undefined8 *)(param_3 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    puVar2 = *(undefined4 **)(param_3 + 0x10);
  }
  *puVar2 = 0xc0026900;
  puVar2[1] = 0x2e0;
  puVar2[2] = param_1;
  puVar2[3] = param_2;
  *(long *)(param_3 + 0x10) = *(long *)(param_3 + 0x10) + 0x10;
  return;
}

