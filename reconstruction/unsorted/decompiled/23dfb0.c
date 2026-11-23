
void FUN_0023dfb0(long *param_1)

{
  long *plVar1;
  long local_28;
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  if (*param_1 != 0) {
    local_28 = *param_1;
    FUN_0023ec10(&DAT_026485c0,param_1,&local_28);
  }
  *param_1 = 0;
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

