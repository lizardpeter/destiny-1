
void FUN_007dcaf0(long param_1)

{
  long lVar1;
  
  FUN_00f8ede0(*(undefined8 *)(param_1 + 0x50));
  lVar1 = *(long *)(param_1 + 0x50);
  if (*(long *)(lVar1 + 0x40) != 0) {
    FUN_00f84db0(lVar1 + 0x40);
  }
  FUN_00f7e5e0(lVar1);
  *(undefined2 *)(lVar1 + 0xc84) = 0;
  *(undefined4 *)(lVar1 + 0xc80) = 0;
  FUN_007dc270(param_1,1);
  return;
}

