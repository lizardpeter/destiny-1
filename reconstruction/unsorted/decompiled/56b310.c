
void FUN_0056b310(byte param_1,undefined8 *param_2)

{
  long *plVar1;
  ulong local_28;
  undefined8 local_20;
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  local_28 = (ulong)param_1;
  local_20 = *param_2;
  FUN_00300230(0x2e,*(undefined4 *)PTR_DAT_019e4c00,&local_28);
  if (*plVar1 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

