
void FUN_00f80e00(long param_1,ulong param_2,undefined4 param_3,uint param_4,undefined4 param_5)

{
  char cVar1;
  undefined4 *puVar2;
  uint uVar3;
  
  puVar2 = *(undefined4 **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar2) >> 2) < 7) {
    cVar1 = (**(code **)(param_1 + 0x18))(param_1,7,*(undefined8 *)(param_1 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    puVar2 = *(undefined4 **)(param_1 + 0x10);
  }
  uVar3 = 0xffff;
  *puVar2 = 0xc0053c00;
  if (0xffff < param_2) {
    uVar3 = 0xfffffffc;
  }
  puVar2[1] = (uint)(0xffff < param_2) << 4 | param_4 & 7;
  puVar2[2] = (uint)param_2 & uVar3;
  puVar2[3] = (uint)(param_2 >> 0x20) & 0xffff;
  puVar2[4] = param_5;
  puVar2[5] = param_3;
  puVar2[6] = 10;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0x1c;
  return;
}

