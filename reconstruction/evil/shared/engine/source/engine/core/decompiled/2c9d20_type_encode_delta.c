
undefined8
FUN_002c9d20(undefined8 param_1,undefined8 param_2,undefined4 param_3,long param_4,byte *param_5,
            undefined4 param_6)

{
  byte bVar1;
  byte *pbVar2;
  uint uVar3;
  
  uVar3 = (*(int *)(param_5 + 8) << 0x12) >> 0x12;
  if ((uVar3 & 0xfffffffe) == 0xfffffffe) {
    bVar1 = 0;
    if (((*(int *)(param_5 + 8) << 4) >> 0x12) + 0x1f >> 5 < 1) goto LAB_002c9d75;
    bVar1 = **(byte **)param_5;
  }
  else {
    bVar1 = 0;
    if (uVar3 != 0) goto LAB_002c9d75;
    bVar1 = *param_5;
  }
  bVar1 = bVar1 & 1;
LAB_002c9d75:
  if (*(uint *)(param_4 + 0x30) < 0x40) {
    *(uint *)(param_4 + 0x30) = *(uint *)(param_4 + 0x30) + 1;
    *(int *)(param_4 + 0x24) = *(int *)(param_4 + 0x24) + 1;
    *(ulong *)(param_4 + 0x28) = *(long *)(param_4 + 0x28) * 2 | (ulong)bVar1;
  }
  else {
    FUN_000733a0(param_4,bVar1,1);
  }
  uVar3 = (*(int *)(param_5 + 8) << 0x12) >> 0x12;
  if ((uVar3 & 0xfffffffe) == 0xfffffffe) {
    if (((*(int *)(param_5 + 8) << 4) >> 0x12) + 0x1f >> 5 < 1) {
      return 1;
    }
    pbVar2 = *(byte **)param_5;
  }
  else {
    pbVar2 = param_5;
    if (uVar3 != 0) {
      return 1;
    }
  }
  if ((*pbVar2 & 1) != 0) {
    FUN_002c7fa0(param_3,param_5,0,param_2,param_4,param_6);
  }
  return 1;
}

