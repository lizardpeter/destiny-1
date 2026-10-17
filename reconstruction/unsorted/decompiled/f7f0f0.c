
void FUN_00f7f0f0(long param_1,uint param_2,undefined8 param_3,uint param_4,undefined8 param_5,
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
  *puVar2 = 0xc0055000;
  puVar2[1] = param_7 << 0x1f | (param_2 & 1) << 0x14 | (param_4 & 3) << 0x1d | 0x4004000;
  puVar2[2] = (int)param_5;
  puVar2[3] = (int)((ulong)param_5 >> 0x20);
  puVar2[4] = (int)param_3;
  puVar2[5] = (int)((ulong)param_3 >> 0x20);
  puVar2[6] = param_6 & 0x1fffff |
              (param_4 & 8) << 0x19 |
              (param_4 & 4) << 0x18 | (param_2 & 8) << 0x1a | (param_2 & 4) << 0x19;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0x1c;
  return;
}

