
void FUN_000ae1e0(undefined4 param_1,int param_2,long param_3,long param_4)

{
  undefined1 uVar1;
  ulong uVar2;
  
  if (0 < param_2) {
    uVar2 = 0;
    do {
      uVar1 = FUN_000ae0c0(uVar2 & 0xffffffff,param_1,param_4);
      *(undefined1 *)(param_3 + uVar2) = uVar1;
      param_4 = param_4 + 0xc0;
      uVar2 = uVar2 + 1;
    } while (param_2 != (int)uVar2);
  }
  return;
}

