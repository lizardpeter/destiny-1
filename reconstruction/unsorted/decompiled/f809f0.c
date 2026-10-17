
void FUN_00f809f0(long param_1,undefined8 param_2,uint param_3,uint param_4)

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
  *(byte *)(param_1 + 0x28) = *(byte *)(param_1 + 0x28) | 1;
  *puVar2 = 0xc0012000;
  puVar2[1] = (uint)param_2 & 0xfffffff0;
  puVar2[2] = (uint)((ulong)param_2 >> 0x20) & 0xff | (param_3 & 1) << 0xc | (param_4 & 1) << 8 |
              0x10000;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0xc;
  return;
}

