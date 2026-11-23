
bool FUN_00641bb0(long param_1)

{
  undefined4 uVar1;
  int iVar2;
  undefined4 uVar3;
  
  *(undefined1 *)(param_1 + 0x254) = 1;
  FUN_00641c10();
  iVar2 = FUN_0063fd60(0,*(undefined4 *)(param_1 + 0x24));
  *(int *)(param_1 + 0x250) = iVar2;
  if (iVar2 != -1) {
    uVar1 = *(undefined4 *)(param_1 + 0x24);
    uVar3 = FUN_0063fdb0();
    FUN_0063ca80(param_1 + 0x158,uVar1,uVar3);
  }
  return iVar2 != -1;
}

