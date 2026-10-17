
void FUN_00950620(undefined8 param_1,undefined4 *param_2,undefined4 param_3,undefined1 param_4)

{
  long *plVar1;
  undefined4 local_20 [2];
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  local_20[0] = *param_2;
  FUN_00950ff0(param_1,local_20,0,param_3,param_4,1);
  if (*plVar1 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

