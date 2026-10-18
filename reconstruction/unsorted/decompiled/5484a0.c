
void FUN_005484a0(uint param_1,undefined8 param_2,undefined4 param_3)

{
  long *plVar1;
  undefined4 uVar2;
  undefined8 local_38;
  undefined8 uStack_30;
  ulong local_28 [3];
  
  plVar1 = DAT_01a1f100;
  local_28[2] = *DAT_01a1f100;
  local_28[1] = 0;
  local_28[0] = (ulong)param_1;
  local_38 = 0;
  uStack_30 = 0;
  uVar2 = FUN_00267270(param_3);
  local_38 = CONCAT44(local_38._4_4_,uVar2);
  FUN_00528c50(1,local_28,2,&local_38);
  if (*plVar1 == local_28[2]) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

