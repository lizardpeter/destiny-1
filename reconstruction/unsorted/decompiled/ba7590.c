
uint FUN_00ba7590(long param_1,long *param_2)

{
  uint uVar1;
  uint uVar2;
  long *plVar3;
  
  plVar3 = (long *)(param_1 + 0x12ec);
  uVar1 = 0xffffffff;
  uVar2 = 0;
  do {
    if (((*(uint *)(param_1 + 0x12dc) >> (uVar2 & 0x1f) & 1) != 0) && (*plVar3 == *param_2)) {
      uVar1 = uVar2;
    }
    plVar3 = plVar3 + 1;
    uVar2 = uVar2 + 1;
  } while (uVar2 != 0x14);
  return uVar1;
}

