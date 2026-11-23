
bool FUN_0057f520(void)

{
  char cVar1;
  undefined1 uVar2;
  long lVar3;
  bool bVar4;
  undefined8 local_18;
  long local_10;
  
  local_10 = *DAT_01a1f100;
  cVar1 = FUN_00244ee0(&local_18);
  bVar4 = false;
  if (cVar1 != '\0') {
    lVar3 = FUN_0057ddd0(local_18);
    bVar4 = lVar3 != 0;
  }
  if (*DAT_01a1f100 == local_10) {
    return bVar4;
  }
  uVar2 = thunk_FUN_012aa7f6();
  return (bool)uVar2;
}

