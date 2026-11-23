
void FUN_008d9950(ushort *param_1,undefined8 param_2)

{
  long *plVar1;
  undefined1 local_38 [8];
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  FUN_000f2e30(local_38,*(undefined4 *)(param_1 + 2));
  FUN_000b0bd0((long)&DAT_01ad5000 + (ulong)*param_1 * DAT_01ad5010 + DAT_01ad5000,param_2);
  FUN_000f2e70(local_38);
  if (*plVar1 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

