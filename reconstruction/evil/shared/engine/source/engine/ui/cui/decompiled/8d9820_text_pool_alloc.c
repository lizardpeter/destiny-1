
undefined8 FUN_008d9820(ushort *param_1,undefined8 param_2,undefined8 param_3)

{
  long *plVar1;
  undefined8 uVar2;
  undefined1 local_40 [8];
  long local_38;
  
  plVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  FUN_000f2e30(local_40,*(undefined4 *)(param_1 + 2));
  uVar2 = FUN_000b0af0((long)&DAT_01ad5000 + (ulong)*param_1 * DAT_01ad5010 + DAT_01ad5000,param_2,
                       param_3);
  FUN_000f2e70(local_40);
  if (*plVar1 == local_38) {
    return uVar2;
  }
  uVar2 = thunk_FUN_012aa7f6();
  return uVar2;
}

