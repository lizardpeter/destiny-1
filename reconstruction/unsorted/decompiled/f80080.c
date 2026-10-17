
void FUN_00f80080(long param_1,undefined4 param_2,int param_3,undefined8 *param_4)

{
  uint uVar1;
  undefined4 *puVar2;
  undefined8 uVar3;
  char cVar4;
  int iVar5;
  
  if (((uint)((ulong)(*(long *)(param_1 + 8) - *(long *)(param_1 + 0x10)) >> 2) < 0xc) &&
     (cVar4 = (**(code **)(param_1 + 0x18))(param_1,0xc,*(undefined8 *)(param_1 + 0x20)),
     cVar4 == '\0')) {
    return;
  }
  uVar1 = *(uint *)(param_1 + 0x28);
  iVar5 = FUN_00f83520(param_2,param_3);
  FUN_00f83520(param_2,param_3 + 7);
  puVar2 = *(undefined4 **)(param_1 + 0x10);
  *puVar2 = 0xc0001000;
  puVar2[1] = 0x68750005;
  *(undefined4 **)(param_1 + 0x10) = puVar2 + 2;
  puVar2[2] = uVar1 & 2 | 0xc0087600;
  puVar2[3] = iVar5 + -0x2c00;
  *(undefined8 *)(puVar2 + 10) = param_4[3];
  *(undefined8 *)(puVar2 + 8) = param_4[2];
  uVar3 = *param_4;
  *(undefined8 *)(puVar2 + 6) = param_4[1];
  *(undefined8 *)(puVar2 + 4) = uVar3;
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0x28;
  return;
}

