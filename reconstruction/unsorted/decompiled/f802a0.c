
void FUN_00f802a0(long param_1,undefined4 param_2,undefined4 param_3,uint param_4)

{
  uint uVar1;
  uint *puVar2;
  char cVar3;
  int iVar4;
  
  if (((uint)((ulong)(*(long *)(param_1 + 8) - *(long *)(param_1 + 0x10)) >> 2) < 3) &&
     (cVar3 = (**(code **)(param_1 + 0x18))(param_1,3,*(undefined8 *)(param_1 + 0x20)),
     cVar3 == '\0')) {
    return;
  }
  uVar1 = *(uint *)(param_1 + 0x28);
  iVar4 = FUN_00f83520(param_2,param_3);
  puVar2 = *(uint **)(param_1 + 0x10);
  *puVar2 = uVar1 & 2 | 0xc0017600;
  puVar2[1] = iVar4 - 0x2c00;
  puVar2[2] = param_4;
  *(uint **)(param_1 + 0x10) = puVar2 + 3;
  return;
}

