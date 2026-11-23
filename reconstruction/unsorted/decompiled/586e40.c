
void FUN_00586e40(long param_1,undefined8 param_2)

{
  undefined *puVar1;
  long *plVar2;
  undefined8 uVar3;
  undefined8 local_38;
  long local_30;
  
  plVar2 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  uVar3 = FUN_0056b260();
  FUN_0056d110(uVar3,param_2);
  puVar1 = PTR_DAT_019e4d70;
  *(undefined1 *)(param_1 + 0x48) = 2;
  local_38 = thunk_FUN_012aac96();
  FUN_00300230(0x31,*(undefined4 *)puVar1,&local_38);
  *(undefined1 *)(param_1 + 0x41e) = 1;
  if (*plVar2 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

