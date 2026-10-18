
void FUN_005763b0(undefined8 param_1,long *param_2)

{
  long *plVar1;
  long lVar2;
  
  (**(code **)(*param_2 + 0x40))(param_2);
  if (*(char *)(DAT_026bc2c0 + 0x8018) != '\0') {
    plVar1 = (long *)FUN_0025a550();
    lVar2 = (**(code **)(*plVar1 + 0x88))(plVar1);
    if (lVar2 != 0) {
      thunk_FUN_0025cc10(param_2);
      return;
    }
  }
  return;
}

