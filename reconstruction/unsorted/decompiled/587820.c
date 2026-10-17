
undefined8 FUN_00587820(void)

{
  long *plVar1;
  undefined8 uVar2;
  long local_28;
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  uVar2 = 0;
  if (DAT_026bc510 != 0) {
    local_28 = FUN_00587710();
    if (local_28 != 0) {
      uVar2 = FUN_00584560(&local_28);
    }
  }
  if (*plVar1 == local_20) {
    return uVar2;
  }
  uVar2 = thunk_FUN_012aa7f6();
  return uVar2;
}

