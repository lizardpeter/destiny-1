
void FUN_00f81090(long param_1,uint param_2,undefined8 param_3,uint param_4)

{
  char cVar1;
  uint *puVar2;
  uint uVar3;
  uint uVar4;
  uint uVar5;
  uint uVar6;
  
  puVar2 = *(uint **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar2) >> 2) < 5) {
    cVar1 = (**(code **)(param_1 + 0x18))(param_1,5,*(undefined8 *)(param_1 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    puVar2 = *(uint **)(param_1 + 0x10);
  }
  uVar3 = *(uint *)(param_1 + 0x28) & 2 | 0xc0034800;
  *puVar2 = uVar3;
  uVar6 = param_2 & 0x3f | 0x600;
  puVar2[1] = uVar6;
  uVar4 = (uint)param_3 & 0xfffffffc;
  puVar2[2] = uVar4;
  uVar5 = (uint)((ulong)param_3 >> 0x20) & 0xff | 0x40000000;
  puVar2[3] = uVar5;
  puVar2[4] = param_4;
  puVar2 = *(uint **)(param_1 + 0x10);
  *puVar2 = uVar3;
  puVar2[1] = uVar6;
  puVar2[2] = uVar4;
  puVar2[3] = uVar5;
  puVar2[4] = param_4;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0x14;
  return;
}

