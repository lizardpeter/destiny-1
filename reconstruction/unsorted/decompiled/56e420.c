
void FUN_0056e420(undefined8 *param_1,undefined8 param_2,int param_3,undefined8 param_4,int param_5)

{
  undefined4 uVar1;
  long lVar2;
  undefined8 uVar3;
  long local_30;
  undefined8 local_28;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  if (param_3 == 3) {
    if ((param_5 == 1) && (lVar2 = FUN_00078970(&DAT_026bc2b8), lVar2 != 0)) {
      FUN_00577a50(lVar2,*param_1);
    }
  }
  else if (param_3 == 4) {
    switch(param_5) {
    case 0:
      FUN_0057e060();
      break;
    case 1:
      uVar3 = FUN_00557c40(&DAT_026bc508);
      uVar3 = FUN_00586750(uVar3,*param_1);
      FUN_002f1dc0(uVar3);
      uVar3 = FUN_00557c40(&DAT_026bc4d8);
      FUN_00585030(uVar3,2);
      break;
    case 3:
      uVar3 = FUN_00557c40(&DAT_026bc508);
      local_28 = FUN_005863c0(uVar3);
      lVar2 = FUN_00586510(uVar3,&local_28);
      local_30 = lVar2;
      uVar3 = FUN_0056b260();
      if (lVar2 != 0) {
        uVar1 = FUN_01009850(uVar3);
        FUN_0056dc00(uVar3,4,uVar1,&local_30);
      }
      break;
    case 4:
      FUN_0056f9d0(param_1,1);
    }
  }
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

