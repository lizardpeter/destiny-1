
bool FUN_00340d10(undefined8 param_1,undefined8 param_2)

{
  long *plVar1;
  undefined1 uVar2;
  int iVar3;
  undefined1 local_60 [64];
  long local_20;
  
  plVar1 = DAT_01a1f100;
  local_20 = *DAT_01a1f100;
  FUN_00101920(param_2,0,local_60);
  iVar3 = FUN_000cdb80(local_60);
  if (*plVar1 == local_20) {
    return iVar3 != -1;
  }
  uVar2 = thunk_FUN_012aa7f6();
  return (bool)uVar2;
}

