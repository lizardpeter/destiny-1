
void FUN_00f7ecb0(undefined4 param_1,undefined4 param_2,long param_3)

{
  char cVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(param_3 + 0x10);
  if ((uint)((ulong)(*(long *)(param_3 + 8) - (long)puVar2) >> 2) < 6) {
    cVar1 = (**(code **)(param_3 + 0x18))(param_3,6,*(undefined8 *)(param_3 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    puVar2 = *(undefined4 **)(param_3 + 0x10);
  }
  *puVar2 = 0xc0016900;
  puVar2[1] = 0x2fb;
  puVar2[2] = param_2;
  puVar2[3] = 0xc0016900;
  puVar2[4] = 0x2fd;
  puVar2[5] = param_1;
  *(undefined4 **)(param_3 + 0x10) = puVar2 + 6;
  return;
}

