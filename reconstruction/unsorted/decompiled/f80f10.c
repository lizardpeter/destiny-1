
void FUN_00f80f10(long param_1,uint param_2,uint param_3,int param_4)

{
  char cVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar2) >> 2) < 7) {
    cVar1 = (**(code **)(param_1 + 0x18))(param_1,7,*(undefined8 *)(param_1 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    puVar2 = *(undefined4 **)(param_1 + 0x10);
  }
  *puVar2 = 0xc0055800;
  puVar2[1] = param_4 << 0x1f |
              (param_2 & 0xb) << 0xf | (param_2 & 0x30) << 0x12 | param_3 & 0x7fffffff;
  puVar2[2] = 1;
  puVar2[3] = 0;
  puVar2[4] = 0;
  puVar2[5] = 0;
  puVar2[6] = 10;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0x1c;
  return;
}

