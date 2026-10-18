
void FUN_0056e330(int param_1,undefined8 *param_2)

{
  long *plVar1;
  long lVar2;
  undefined8 uVar3;
  undefined8 local_28;
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  if (param_1 == 4) {
    lVar2 = FUN_00021860(&DAT_026bc820);
    if (lVar2 != 0) {
      FUN_00590940(lVar2);
    }
    lVar2 = FUN_00557c40(&DAT_026bc508);
    if (lVar2 != 0) {
      FUN_00586920(lVar2,*param_2);
    }
    FUN_005755e0(4);
    uVar3 = FUN_00078970(&DAT_026bc380);
    FUN_0057bea0(uVar3);
    uVar3 = FUN_00557c40(&DAT_026bc4d8);
    FUN_00585030(uVar3,2);
    FUN_003c9b50();
  }
  else if (param_1 == 0) {
    lVar2 = FUN_00078970(&DAT_026bc820);
    if (lVar2 != 0) {
      local_28 = *param_2;
      FUN_0058e410(lVar2,&local_28);
    }
  }
  if (*plVar1 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

