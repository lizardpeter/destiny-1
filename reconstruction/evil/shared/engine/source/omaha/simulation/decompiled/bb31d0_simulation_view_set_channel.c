
void FUN_00bb31d0(long param_1,undefined8 param_2,undefined8 param_3)

{
  undefined8 uVar1;
  
  FUN_00ba12c0(param_2,*(undefined4 *)(*(long *)(param_1 + 0x48) + 8),param_1,param_3);
  *(undefined8 *)(param_1 + 0x68) = param_2;
  *(undefined4 *)(param_1 + 0x70) = 0;
  uVar1 = FUN_0013dfd0(param_2);
  FUN_00b62000(uVar1,*(undefined8 *)(*(long *)(param_1 + 0x48) + 0x20),
               *(undefined8 *)(*(long *)(param_1 + 0x48) + 0x10),param_1 + 0xc40,param_1 + 0x140,
               param_1 + 0x100,param_1 + 0xa8,param_1 + 0xc20);
  FUN_00b5e5f0(param_1 + 0xa8);
  *(undefined1 *)(param_1 + 0xa4) = 0;
  FUN_00bb3280(param_1,*(undefined4 *)(param_1 + 0x74),*(undefined4 *)(param_1 + 0x78));
  return;
}

