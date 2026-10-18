
void FUN_00106ed0(undefined4 *param_1)

{
  long *plVar1;
  undefined8 uVar2;
  undefined4 local_20 [2];
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  local_20[0] = *param_1;
  uVar2 = 0;
  if ((ulong)DAT_025d6ff8 != 0) {
    uVar2 = *(undefined8 *)(&DAT_01ad5030 + (ulong)DAT_025d6ff8 * DAT_01ad5010 + DAT_01ad5000);
  }
  FUN_0100d2e0(uVar2,local_20);
  if (*plVar1 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

