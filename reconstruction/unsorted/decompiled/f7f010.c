
void FUN_00f7f010(long param_1,undefined8 param_2,undefined4 *param_3,int param_4,uint param_5,
                 uint param_6)

{
  long lVar1;
  char cVar2;
  uint *puVar3;
  undefined4 *puVar4;
  uint uVar5;
  
  puVar3 = *(uint **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar3) >> 2) < param_4 + 4U) {
    cVar2 = (**(code **)(param_1 + 0x18))(param_1,param_4 + 4U,*(undefined8 *)(param_1 + 0x20));
    if (cVar2 == '\0') {
      return;
    }
    puVar3 = *(uint **)(param_1 + 0x10);
  }
  *puVar3 = param_4 * 0x10000 + 0x20000U | 0xc0003700;
  puVar3[1] = (param_5 & 3) << 0x19 | (param_6 & 1) << 0x14 | 0x200;
  puVar3[2] = (uint)param_2 & 0xfffffffc;
  puVar3[3] = (uint)((ulong)param_2 >> 0x20);
  lVar1 = *(long *)(param_1 + 0x10);
  puVar4 = (undefined4 *)(lVar1 + 0x10);
  *(undefined4 **)(param_1 + 0x10) = puVar4;
  if (param_4 != 0) {
    uVar5 = param_4 - 1;
    do {
      *puVar4 = *param_3;
      puVar4 = puVar4 + 1;
      param_3 = param_3 + 1;
      param_4 = param_4 + -1;
    } while (param_4 != 0);
    *(ulong *)(param_1 + 0x10) = lVar1 + 0x14 + (ulong)uVar5 * 4;
  }
  return;
}

