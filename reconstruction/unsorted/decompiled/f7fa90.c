
void FUN_00f7fa90(long param_1,uint param_2,uint param_3)

{
  uint uVar1;
  char cVar2;
  undefined4 *puVar3;
  
  uVar1 = (uint)(param_2 == 0) * 3 + 3;
  puVar3 = *(undefined4 **)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar3) >> 2) < uVar1) {
    cVar2 = (**(code **)(param_1 + 0x18))(param_1,uVar1,*(undefined8 *)(param_1 + 0x20));
    if (cVar2 == '\0') {
      return;
    }
    puVar3 = *(undefined4 **)(param_1 + 0x10);
  }
  *puVar3 = 0xc0016900;
  puVar3[1] = 0x290;
  puVar3[2] = (param_3 & 3) << 4 | param_2 & 0xffffffcf;
  *(undefined4 **)(param_1 + 0x10) = puVar3 + 3;
  if (param_2 == 0) {
    puVar3[3] = 0xc0016900;
    puVar3[4] = 0x2e5;
    puVar3[5] = 0;
    *(undefined4 **)(param_1 + 0x10) = puVar3 + 6;
  }
  return;
}

