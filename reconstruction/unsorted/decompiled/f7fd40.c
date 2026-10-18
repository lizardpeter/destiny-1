
void FUN_00f7fd40(long param_1,undefined4 param_2,undefined4 param_3,uint param_4,uint param_5,
                 uint param_6,int param_7)

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
  puVar2[1] = param_7 << 0x1f |
              (param_6 | param_4) & 0x7fffffff | (param_5 & 0xb) << 0xf | (param_5 & 0x30) << 0x12;
  puVar2[2] = param_3;
  puVar2[3] = 0;
  puVar2[4] = param_2;
  puVar2[5] = 0;
  puVar2[6] = 10;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0x1c;
  return;
}

