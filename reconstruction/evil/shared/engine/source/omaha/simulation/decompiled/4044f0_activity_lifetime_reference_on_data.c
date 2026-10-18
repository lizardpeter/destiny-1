
void FUN_004044f0(long param_1,undefined4 *param_2)

{
  long *plVar1;
  undefined1 *puVar2;
  undefined4 local_30 [2];
  undefined8 local_28;
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  local_30[0] = *param_2;
  local_28 = *(undefined8 *)(param_2 + 2);
  puVar2 = (undefined1 *)FUN_00078970(local_30,*(undefined4 *)PTR_DAT_019b2b18);
  *(undefined1 *)(param_1 + 0x1ac) = *puVar2;
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

