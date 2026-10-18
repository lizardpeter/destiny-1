
void FUN_00f80a80(long param_1)

{
  char cVar1;
  undefined8 *puVar2;
  
  puVar2 = *(undefined8 **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar2) >> 2) < 3) {
    cVar1 = (**(code **)(param_1 + 0x18))(param_1,3,*(undefined8 *)(param_1 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    puVar2 = *(undefined8 **)(param_1 + 0x10);
  }
  *(byte *)(param_1 + 0x28) = *(byte *)(param_1 + 0x28) & 0xfe;
  *puVar2 = 0xc0012000;
  *(undefined4 *)(puVar2 + 1) = 0;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0xc;
  return;
}

