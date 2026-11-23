
undefined8 FUN_002a5450(long param_1,int param_2)

{
  return CONCAT71((int7)((ulong)((long)param_2 * 0x250) >> 8),
                  *(char *)(param_1 + 0x250 + (long)param_2 * 0x250) != '\0');
}

