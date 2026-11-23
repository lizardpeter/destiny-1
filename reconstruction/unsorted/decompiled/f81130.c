
void FUN_00f81130(long param_1,uint param_2)

{
  char cVar1;
  uint *puVar2;
  
  if (((uint)((ulong)(*(long *)(param_1 + 8) - *(long *)(param_1 + 0x10)) >> 2) < param_2) &&
     (cVar1 = (**(code **)(param_1 + 0x18))(param_1,param_2,*(undefined8 *)(param_1 + 0x20)),
     cVar1 == '\0')) {
    return;
  }
  if (param_2 != 0) {
    if (param_2 == 1) {
      puVar2 = *(uint **)(param_1 + 0x10);
      *puVar2 = 0x80000000;
    }
    else {
      puVar2 = *(uint **)(param_1 + 0x10);
      *puVar2 = param_2 * 0x10000 + 0x3ffe0000 | 0xc0001000;
      puVar2[1] = 0;
    }
    *(uint **)(param_1 + 0x10) = puVar2 + param_2;
  }
  return;
}

