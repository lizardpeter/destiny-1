
void FUN_00f80440(long param_1,uint param_2,int param_3,uint param_4,int param_5)

{
  char cVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar2) >> 2) < 4) {
    cVar1 = (**(code **)(param_1 + 0x18))(param_1,4,*(undefined8 *)(param_1 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    puVar2 = *(undefined4 **)(param_1 + 0x10);
  }
  *puVar2 = 0xc0026900;
  puVar2[1] = 0xc;
  puVar2[2] = param_2 & 0xffff | param_3 << 0x10;
  puVar2[3] = param_4 & 0xffff | param_5 << 0x10;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0x10;
  return;
}

