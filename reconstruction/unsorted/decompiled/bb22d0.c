
void FUN_00bb22d0(undefined8 param_1,undefined8 *param_2)

{
  long *plVar1;
  undefined8 local_5078;
  undefined8 uStack_5070;
  undefined1 local_5068 [8];
  undefined1 local_5060 [20536];
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  FUN_01018410(local_5060);
  uStack_5070 = *param_2;
  local_5078 = param_1;
  thunk_FUN_012aa7c6(local_5068,param_2 + 1,0x5038);
  FUN_00300230(0x1b,*(undefined4 *)PTR_DAT_019b4718,&local_5078);
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

