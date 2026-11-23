
void FUN_0056dfa0(undefined8 param_1,char *param_2)

{
  long *plVar1;
  undefined8 local_20;
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  if (DAT_026bacc0 != 0) {
    local_20 = *(undefined8 *)(param_2 + 8);
    FUN_0056bd50(DAT_026bacc0,(int)*param_2,&local_20);
  }
  if (*plVar1 == local_18) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

