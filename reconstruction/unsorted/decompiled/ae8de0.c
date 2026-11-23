
void FUN_00ae8de0(void)

{
  long lVar1;
  char cVar2;
  long lVar3;
  undefined8 local_28;
  long local_20;
  
  lVar1 = DAT_027be860;
  local_20 = *DAT_01a1f100;
  local_28 = FUN_00001df0();
  *(undefined1 *)(lVar1 + 0x20) = 0;
  cVar2 = FUN_00244ee0(&local_28);
  if (cVar2 != '\0') {
    lVar3 = FUN_0057ddd0(local_28);
    if (lVar3 != 0) {
      *(undefined1 *)(lVar1 + 0x20) = *(undefined1 *)(lVar3 + 0x15);
    }
  }
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

