
bool FUN_00642a30(long param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  FUN_00642a80();
  iVar2 = FUN_0063fd60(2,*(undefined4 *)(param_1 + 0x24));
  *(int *)(param_1 + 0x158) = iVar2;
  if (iVar2 != -1) {
    uVar1 = *(undefined4 *)(param_1 + 0x24);
    uVar3 = FUN_0063fdd0();
    FUN_0063ca80(param_1 + 0x60,uVar1,uVar3);
  }
  return iVar2 != -1;
}

