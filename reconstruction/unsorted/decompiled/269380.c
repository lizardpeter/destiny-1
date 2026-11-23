
undefined8 FUN_00269380(long param_1)

{
  return CONCAT71(*(char *)(param_1 + 0x10) >> 7,
                  *(long *)(*(long *)(param_1 + 8) + (long)*(char *)(param_1 + 0x10) * 8) != 0);
}

