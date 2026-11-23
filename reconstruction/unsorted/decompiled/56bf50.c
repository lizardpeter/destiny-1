
undefined4 FUN_0056bf50(long param_1,char param_2,long *param_3)

{
  undefined4 *puVar1;
  
  for (puVar1 = (undefined4 *)(param_1 + 0x9c);
      (*(char *)(puVar1 + -0xf) != param_2 || (*(long *)(puVar1 + -7) != *param_3));
      puVar1 = puVar1 + 0x10) {
  }
  return *puVar1;
}

