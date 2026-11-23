
void FUN_007e03a0(long param_1)

{
  undefined8 uVar1;
  undefined4 *puVar2;
  
  uVar1 = *(undefined8 *)(param_1 + 0x50);
  puVar2 = (undefined4 *)FUN_00f7feb0(uVar1,4,3);
  *puVar2 = 0;
  FUN_00f80c90(uVar1,4,0,puVar2,1,1,0,0);
  FUN_00f80e00(uVar1,puVar2,0xffffffff,3,1);
  FUN_00f80f10(uVar1,0x38,0,1);
  return;
}

