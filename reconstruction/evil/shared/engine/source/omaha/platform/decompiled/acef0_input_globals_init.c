
bool FUN_000acef0(void)

{
  long *plVar1;
  undefined1 uVar2;
  char *local_28;
  undefined4 local_20;
  undefined1 local_1c;
  undefined1 local_1b;
  long local_18;
  
  plVar1 = DAT_01a1f100;
  local_18 = *DAT_01a1f100;
  thunk_FUN_012aa986(&DAT_01ad40d0,0,0xd30);
  DAT_01ad40d0 = '\x01';
  local_28 = s_keyboard_buffer_016136ad;
  local_20 = 0;
  local_1c = 0;
  local_1b = 0;
  DAT_01ad4df8 = thunk_FUN_000f6b70(&local_28);
  FUN_000f6550();
  FUN_000ada40();
  FUN_000acf80(1);
  if (*plVar1 == local_18) {
    return DAT_01ad40d0 != '\0';
  }
  uVar2 = thunk_FUN_012aa7f6();
  return (bool)uVar2;
}

