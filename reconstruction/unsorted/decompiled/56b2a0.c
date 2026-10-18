
void FUN_0056b2a0(byte param_1,undefined8 *param_2,byte param_3)

{
  long *plVar1;
  ulong local_38;
  undefined8 uStack_30;
  ulong local_28;
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  local_38 = (ulong)param_1;
  uStack_30 = *param_2;
  local_28 = (ulong)param_3;
  FUN_00300230(0x2d,*(undefined4 *)PTR_DAT_019e4bf8,&local_38);
  if (*plVar1 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

