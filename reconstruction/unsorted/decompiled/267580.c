
undefined8 FUN_00267580(long param_1)

{
  long *plVar1;
  int *piVar2;
  
  plVar1 = (long *)FUN_0025a550();
  piVar2 = (int *)(**(code **)(*plVar1 + 0xb8))(plVar1);
  return CONCAT71((int7)(int3)((uint)*piVar2 >> 8),
                  (ulong)(long)*(char *)(param_1 + 0x10) < (ulong)(long)*piVar2);
}

