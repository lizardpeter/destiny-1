
long FUN_0029a5e0(long param_1)

{
  undefined8 uVar1;
  long lVar2;
  
  if ((*(byte *)(param_1 + 0x130) & 0x40) != 0) {
    uVar1 = FUN_00021860(*(undefined8 *)(param_1 + 0xe58));
    lVar2 = FUN_002a2980(uVar1);
    return lVar2 + 0x60;
  }
  return 0;
}

