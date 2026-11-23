
void FUN_000b0f60(long param_1,long param_2,long param_3,uint *param_4,uint param_5)

{
  long lVar1;
  long lVar2;
  long local_40;
  
  lVar2 = (long)param_4 - *(long *)(param_1 + 0x30);
  if (*(code **)(param_1 + 200) != (code *)0x0) {
    (**(code **)(param_1 + 200))(param_4,0x20);
  }
  param_4[6] = 0;
  param_4[7] = 0;
  param_4[4] = 0;
  param_4[5] = 0;
  param_4[2] = 0;
  param_4[3] = 0;
  param_4[0] = 0;
  param_4[1] = 0;
  *param_4 = param_5 & 0xfffffff;
  *(long *)(param_4 + 6) = param_2;
  *(long *)(param_4 + 4) = param_3;
  local_40 = 0;
  lVar1 = 0;
  if (DAT_01ad4f48 != param_2) {
    lVar1 = *(long *)(param_1 + 0x30) + param_2;
  }
  if (DAT_01ad4f48 != param_3) {
    local_40 = param_3 + *(long *)(param_1 + 0x30);
  }
  if (lVar1 == 0) {
    *(long *)(param_1 + 0x80) = lVar2;
    *(long *)(param_1 + 0x98) = lVar2;
  }
  else {
    if (*(code **)(param_1 + 200) != (code *)0x0) {
      (**(code **)(param_1 + 200))(lVar1,0x20);
    }
    if (*(long *)(param_1 + 0x98) == param_2) {
      *(long *)(param_1 + 0x98) = lVar2;
    }
    *(long *)(lVar1 + 0x10) = lVar2;
    if (*(code **)(param_1 + 0xd0) != (code *)0x0) {
      (**(code **)(param_1 + 0xd0))(lVar1,0x20);
    }
  }
  if (local_40 == 0) {
    *(long *)(param_1 + 0x88) = lVar2;
  }
  else {
    if (*(code **)(param_1 + 200) != (code *)0x0) {
      (**(code **)(param_1 + 200))(local_40,0x20);
    }
    *(long *)(local_40 + 0x18) = lVar2;
    if (*(code **)(param_1 + 0xd0) != (code *)0x0) {
      (**(code **)(param_1 + 0xd0))(local_40,0x20);
    }
  }
  if (*(code **)(param_1 + 0xd0) != (code *)0x0) {
                    /* WARNING: Could not recover jumptable at 0x000b10d1. Too many branches */
                    /* WARNING: Treating indirect jump as call */
    (**(code **)(param_1 + 0xd0))(param_4,0x20);
    return;
  }
  return;
}

