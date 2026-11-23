
undefined * FUN_007dca10(long param_1,long param_2)

{
  long lVar1;
  undefined8 *puVar2;
  
  puVar2 = &DAT_015b6068;
  lVar1 = *(long *)(param_1 + 0x18);
  if (lVar1 == DAT_015b6068) {
    *(long *)(param_1 + 0x18) = lVar1;
  }
  else {
    puVar2 = (undefined8 *)&DAT_015b6000;
    if (lVar1 != param_2) {
      return &DAT_015b6000;
    }
    *(long *)(param_1 + 0x18) = DAT_015b6068;
  }
  return (undefined *)CONCAT71((int7)((ulong)puVar2 >> 8),1);
}

