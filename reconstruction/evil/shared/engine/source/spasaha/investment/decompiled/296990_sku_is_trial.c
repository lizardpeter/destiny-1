
bool FUN_00296990(void)

{
  long *plVar1;
  undefined1 uVar2;
  int local_1c;
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  thunk_FUN_012ab776(0,&local_1c);
  if (*plVar1 == local_18) {
    return local_1c != 3;
  }
  uVar2 = thunk_FUN_012aa7f6();
  return (bool)uVar2;
}

