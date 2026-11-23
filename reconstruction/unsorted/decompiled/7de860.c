
void FUN_007de860(long param_1,int param_2)

{
  long lVar1;
  
  if (*(int *)(FUN_000025f0 + param_1) != param_2) {
    lVar1 = *(long *)(param_1 + 0x50);
    *(int *)(lVar1 + 0x3a8) = param_2;
    FUN_00f7fe20(lVar1,param_2);
    if ((param_2 != 0xad) && (param_2 != 0xb0)) {
      FUN_00f7fa90(*(undefined8 *)(param_1 + 0x50),0,0);
    }
    *(int *)(FUN_000025f0 + param_1) = param_2;
  }
  return;
}

