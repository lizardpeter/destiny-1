
void FUN_0056b370(undefined1 param_1,undefined1 param_2,undefined8 *param_3)

{
  long *plVar1;
  undefined8 local_28;
  undefined8 local_20;
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  local_28 = (ulong)CONCAT11(param_2,param_1);
  local_20 = *param_3;
  FUN_00300230(0x2f,*(undefined4 *)PTR_DAT_019e4c08,&local_28);
  if (*plVar1 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

