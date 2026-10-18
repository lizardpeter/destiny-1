
undefined8 FUN_0056bec0(long param_1,char param_2,long *param_3)

{
  long lVar1;
  long lVar2;
  
  lVar1 = 0x60;
  while ((*(char *)(param_1 + lVar1) != param_2 || (*(long *)(param_1 + 0x20 + lVar1) != *param_3)))
  {
    lVar1 = lVar1 + 0x40;
    lVar2 = 0;
    if ((int)lVar1 == 0x40a0) {
LAB_0056bef7:
      return CONCAT71((int7)((ulong)lVar1 >> 8),lVar2 != 0);
    }
  }
  lVar2 = param_1 + lVar1;
  goto LAB_0056bef7;
}

