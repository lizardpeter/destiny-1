
void FUN_0102cea0(undefined8 *param_1,undefined4 param_2,undefined8 param_3,undefined8 param_4,
                 undefined8 param_5)

{
  long *plVar1;
  uint uVar2;
  undefined8 uVar3;
  undefined4 local_40 [2];
  long local_38;
  
  plVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  local_40[0] = 0xffffffff;
  uVar2 = FUN_00072c70(param_4,6);
  (*(code *)(&PTR_FUN_019131b0)[uVar2])(local_40,param_2,param_3,param_4,param_5);
  uVar3 = FUN_00071fe0(local_40[0]);
  *param_1 = uVar3;
  if (*plVar1 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

