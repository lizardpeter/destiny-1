
undefined4 FUN_0054d110(undefined8 param_1,short param_2)

{
  undefined4 uVar1;
  int *piVar2;
  long lVar3;
  
  piVar2 = (int *)FUN_00549570();
  uVar1 = 0xffffffff;
  if ((ulong)(long)param_2 < (ulong)(long)*piVar2) {
    lVar3 = (long)param_2 * 0x10;
    if ((long)piVar2 + lVar3 + *(long *)(piVar2 + 2) + 0x18 != 0) {
      uVar1 = *(undefined4 *)((long)piVar2 + lVar3 + *(long *)(piVar2 + 2) + 0x20);
    }
  }
  return uVar1;
}

