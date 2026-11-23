
void FUN_00765fb0(uint param_1)

{
  long *plVar1;
  undefined4 local_30 [2];
  undefined4 local_28 [2];
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  FUN_007680c0();
  *(uint *)(DAT_026c9d30 + 0x23c) = param_1;
  local_28[0] = DAT_026c9d38;
  local_30[0] = *(undefined4 *)(&DAT_026c9d40 + (ulong)param_1 * 4);
  FUN_007bc410(local_28,local_30);
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

