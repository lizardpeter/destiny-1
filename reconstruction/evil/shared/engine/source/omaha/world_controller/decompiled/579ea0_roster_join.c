
void FUN_00579ea0(undefined8 param_1,undefined8 *param_2,undefined1 param_3,undefined1 param_4,
                 undefined8 param_5)

{
  long *plVar1;
  undefined8 local_80;
  undefined8 uStack_78;
  undefined8 uStack_70;
  undefined8 uStack_68;
  undefined8 local_60;
  undefined8 local_58;
  undefined8 local_50;
  undefined8 local_48;
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  local_80 = *param_2;
  uStack_78 = param_2[1];
  uStack_70 = param_2[2];
  uStack_68 = param_2[3];
  local_60 = param_2[4];
  local_58 = param_2[5];
  local_50 = (ulong)CONCAT11(param_4,param_3);
  local_48 = param_5;
  FUN_00300230(0x24,*(undefined4 *)PTR_DAT_019e4d00,&local_80);
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

