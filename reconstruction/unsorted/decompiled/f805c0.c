
void FUN_00f805c0(long param_1,undefined8 param_2,int param_3,uint param_4)

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
  *puVar2 = 0xc0016900;
  puVar2[1] = 1;
  puVar2[2] = param_3 * 2 & 2U | (param_4 & 7) << 4 | 0x11000100;
  *(undefined4 **)(param_1 + 0x10) = puVar2 + 3;
  return;
}

