
void FUN_00f7eaf0(undefined4 param_1,long param_2)

{
  char cVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(param_2 + 0x10);
  if ((uint)((ulong)(*(long *)(param_2 + 8) - (long)puVar2) >> 2) < 3) {
    cVar1 = (**(code **)(param_2 + 0x18))(param_2,3,*(undefined8 *)(param_2 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    puVar2 = *(undefined4 **)(param_2 + 0x10);
  }
  *puVar2 = 0xc0016900;
  puVar2[1] = 0xb;
  puVar2[2] = param_1;
  *(undefined4 **)(param_2 + 0x10) = puVar2 + 3;
  return;
}

