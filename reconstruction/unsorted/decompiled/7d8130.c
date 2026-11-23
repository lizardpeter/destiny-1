
undefined8 FUN_007d8130(long param_1,undefined4 *param_2)

{
  long *plVar1;
  long lVar2;
  undefined8 uVar3;
  undefined4 local_30 [2];
  undefined8 local_28;
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  local_30[0] = *param_2;
  local_28 = *(undefined8 *)(param_2 + 2);
  lVar2 = FUN_00078970(local_30,*(undefined4 *)PTR_DAT_0198eb00);
  *(undefined4 *)(param_1 + 0x30) = *(undefined4 *)(lVar2 + 0xc);
  if (*plVar1 == local_20) {
    return CONCAT71((int7)((ulong)*plVar1 >> 8),1);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

