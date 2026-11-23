
void FUN_0102c320(undefined8 *param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  long *plVar1;
  char cVar2;
  undefined4 uVar3;
  undefined4 local_38 [2];
  undefined4 local_30 [2];
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  cVar2 = FUN_00073430(param_4);
  if (cVar2 == '\0') {
    param_1[1] = 0;
    *param_1 = 0;
    *(undefined4 *)param_1 = 0xffffffff;
    *(undefined4 *)(param_1 + 2) = 0xffffffff;
  }
  else {
    cVar2 = FUN_00073430(param_4);
    if (cVar2 == '\0') {
      FUN_000730b0(param_4,param_1,0xc0);
    }
    else {
      local_30[0] = 0;
      local_38[0] = 0;
      FUN_000730b0(param_4,local_30,0x20);
      FUN_000730b0(param_4,local_38,0x20);
      uVar3 = FUN_00072c70(param_4,0xc);
      FUN_00073ed0(param_1,local_30[0],uVar3,local_38[0]);
    }
  }
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

