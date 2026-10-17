
undefined8 FUN_007dc9e0(long param_1)

{
  undefined8 uVar1;
  
  if (*(long *)(param_1 + 0x18) == DAT_015b6068) {
    uVar1 = FUN_000f7c30();
    *(undefined8 *)(param_1 + 0x18) = uVar1;
  }
  return 0;
}

