
bool FUN_000f5280(undefined8 param_1,int param_2)

{
  long *plVar1;
  undefined1 uVar2;
  int iVar3;
  int local_1c;
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  local_1c = param_2 * 1000;
  iVar3 = thunk_FUN_012ab346(param_1,1,&local_1c);
  if (*plVar1 == local_18) {
    return iVar3 == 0;
  }
  uVar2 = thunk_FUN_012aa7f6();
  return (bool)uVar2;
}

