
void FUN_0058e9a0(long param_1)

{
  undefined8 uVar1;
  char cVar2;
  undefined4 uVar3;
  
  cVar2 = FUN_00906e00();
  uVar3 = 0xffffffff;
  if (cVar2 != '\0') {
    uVar3 = FUN_005916f0();
  }
  cVar2 = FUN_005884b0(0,uVar3);
  if (cVar2 != '\0') {
    uVar1 = *(undefined8 *)(param_1 + 8);
    FUN_0058d940(uVar1);
    FUN_0058dae0(uVar1);
    return;
  }
  cVar2 = FUN_005884b0(1,uVar3);
  if (cVar2 != '\0') {
    FUN_0058f840(*(undefined8 *)(param_1 + 0x10));
    return;
  }
  return;
}

