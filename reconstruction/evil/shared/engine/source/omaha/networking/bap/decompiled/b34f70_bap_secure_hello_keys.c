
void FUN_00b34f70(long param_1,undefined8 param_2,undefined8 param_3)

{
  char cVar1;
  undefined1 uVar2;
  
  cVar1 = FUN_0006c530(param_1,param_2,0x10);
  if (cVar1 == '\0') {
    uVar2 = 0;
  }
  else {
    uVar2 = FUN_0006d490(param_1 + 0x20,param_3,0x10);
  }
  *(undefined1 *)(param_1 + 0x50) = uVar2;
  return;
}

