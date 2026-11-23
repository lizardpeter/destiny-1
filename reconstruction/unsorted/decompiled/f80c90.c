
void FUN_00f80c90(long param_1,uint param_2,uint param_3,undefined8 param_4,int param_5,
                 undefined8 param_6,uint param_7,uint param_8)

{
  char cVar1;
  undefined4 *puVar2;
  
  puVar2 = *(undefined4 **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar2) >> 2) < 6) {
    cVar1 = (**(code **)(param_1 + 0x18))(param_1,6,*(undefined8 *)(param_1 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    puVar2 = *(undefined4 **)(param_1 + 0x10);
  }
  *puVar2 = 0xc0044700;
  puVar2[1] = (param_8 & 3) << 0x19 |
              (param_7 & 0x3f) << 0xc | (param_3 & 0x10) << 0x17 | param_2 & 0x3f | 0x500;
  puVar2[2] = (uint)param_4 & 0xfffffff8;
  puVar2[3] = (uint)((ulong)param_4 >> 0x20) & 0xffff | (param_3 & 1) << 0x10 | param_5 << 0x1d;
  puVar2[4] = (int)param_6;
  puVar2[5] = (int)((ulong)param_6 >> 0x20);
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0x18;
  return;
}

