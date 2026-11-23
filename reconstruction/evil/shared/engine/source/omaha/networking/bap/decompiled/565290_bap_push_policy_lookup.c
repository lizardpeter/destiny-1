
undefined8 * FUN_00565290(int param_1)

{
  undefined8 *puVar1;
  int iVar2;
  undefined **ppuVar3;
  uint uVar4;
  
  uVar4 = 0;
  ppuVar3 = &PTR_PTR_0193db30;
  do {
    if (0xc < uVar4) {
      return (undefined8 *)0x0;
    }
    puVar1 = (undefined8 *)*ppuVar3;
    iVar2 = (**(code **)*puVar1)(puVar1);
    ppuVar3 = ppuVar3 + 1;
    uVar4 = uVar4 + 1;
  } while (iVar2 != param_1);
  return puVar1;
}

