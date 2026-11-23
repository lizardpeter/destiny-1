
undefined8 FUN_002b8640(undefined8 *param_1,undefined8 *param_2)

{
  long *plVar1;
  undefined8 uVar2;
  undefined8 local_48;
  undefined8 local_40;
  undefined4 local_38;
  undefined8 local_30;
  undefined8 local_28;
  undefined4 local_20;
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  uVar2 = 1;
  if (param_2 != (undefined8 *)0x0) {
    local_20 = *(undefined4 *)(param_1 + 2);
    local_30 = *param_1;
    local_28 = param_1[1];
    local_38 = *(undefined4 *)(param_2 + 2);
    local_48 = *param_2;
    local_40 = param_2[1];
    uVar2 = thunk_FUN_012aa826(&local_30,&local_48,0x10);
  }
  if (*plVar1 == local_18) {
    return uVar2;
  }
  uVar2 = thunk_FUN_012aa7f6();
  return uVar2;
}

