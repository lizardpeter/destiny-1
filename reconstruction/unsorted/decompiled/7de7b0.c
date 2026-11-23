
void FUN_007de7b0(long param_1,long param_2)

{
  long lVar1;
  long lVar2;
  
  if (*(long *)(param_1 + 0x1d30) != param_2) {
    if (param_2 == 0) {
      lVar1 = *(long *)(param_1 + 0x50);
      lVar2 = 0;
    }
    else {
      lVar1 = *(long *)(param_1 + 0x50);
      lVar2 = param_2;
    }
    FUN_00f8b8c0(lVar1 + 0xc0,lVar2);
    *(long *)(param_1 + 0x1d30) = param_2;
  }
  return;
}

