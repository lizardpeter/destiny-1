
uint * FUN_00f7feb0(long param_1,ulong param_2,int param_3)

{
  int iVar1;
  int iVar2;
  char cVar3;
  ulong uVar4;
  uint *puVar5;
  ulong uVar6;
  uint uVar7;
  uint *puVar8;
  ulong uVar9;
  
  uVar4 = (ulong)((1 << ((byte)param_3 & 0x1f)) + -1);
  iVar1 = (int)((param_2 & 0xffffffff) + 3 >> 2);
  puVar5 = *(uint **)(param_1 + 0x10);
  do {
    puVar8 = puVar5;
    uVar6 = ((long)puVar8 + uVar4 + 8 & (uVar4 ^ 0x3ffffffff)) - (long)(puVar8 + 2);
    uVar9 = uVar6 >> 2;
    iVar2 = (int)uVar9;
    uVar7 = iVar1 + 2 + iVar2;
    puVar5 = puVar8;
    if ((uint)((ulong)(*(long *)(param_1 + 8) - (long)puVar8) >> 2) < uVar7) {
      cVar3 = (**(code **)(param_1 + 0x18))(param_1,uVar7,*(undefined8 *)(param_1 + 0x20));
      if (cVar3 == '\0') {
        return (uint *)0x0;
      }
      puVar5 = *(uint **)(param_1 + 0x10);
    }
  } while (puVar8 != puVar5);
  *puVar8 = (iVar1 + iVar2) * 0x10000 | 0xc0001000;
  puVar8[1] = param_3 << 0xc | 0x68750000;
  if (iVar2 != 0) {
    thunk_FUN_012aa986(puVar8 + 2,0,uVar6 & 0x3fffffffc);
    puVar8 = *(uint **)(param_1 + 0x10);
  }
  *(uint **)(param_1 + 0x10) = puVar8 + uVar7;
  return puVar8 + (uVar9 & 0xffffffff) + 2;
}

