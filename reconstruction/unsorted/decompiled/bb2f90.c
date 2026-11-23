
void FUN_00bb2f90(long param_1,undefined8 param_2,undefined4 param_3)

{
  undefined8 uVar1;
  undefined8 uVar2;
  
  *(undefined4 *)(param_1 + 0x50) = param_3;
  *(undefined8 *)(param_1 + 0x48) = param_2;
  uVar1 = FUN_00ba2ba0(param_2);
  uVar2 = FUN_00ba2b80(*(undefined8 *)(param_1 + 0x48));
  *(long *)(param_1 + 0xc40) = param_1;
  FUN_00b60690(param_1 + 0x100,*(undefined4 *)(param_1 + 0x50),uVar1);
  FUN_00b5fa60(uVar1,*(undefined4 *)(param_1 + 0x50),param_1 + 0x100);
  FUN_00b4dfb0(param_1 + 0x140,*(undefined8 *)(param_1 + 0x48),param_1 + 0xc40);
  FUN_00b61820(param_1 + 0xc20,*(undefined8 *)(param_1 + 0x48),*(undefined4 *)(param_1 + 0x50));
  FUN_00b5ba60(param_1 + 0xa8,*(undefined4 *)(param_1 + 0x50),uVar2);
  FUN_00b506b0(uVar2,*(undefined4 *)(param_1 + 0x50),param_1 + 0xa8);
  *(undefined1 *)(param_1 + 0xb1) = 1;
  *(undefined1 *)(param_1 + 0x10a) = 1;
  uVar1 = FUN_00058050(param_2);
  FUN_00bb6ba0(uVar1,param_1);
  uVar1 = DAT_026553b0;
  if (DAT_026553a8 == '\0') {
    uVar1 = FUN_000694d0();
  }
  *(undefined8 *)(param_1 + 0x38) = uVar1;
  return;
}

