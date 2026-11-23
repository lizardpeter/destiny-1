
void FUN_00574f10(void)

{
  long lVar1;
  char cVar2;
  
  lVar1 = DAT_026bc068;
  FUN_01018280(DAT_026bc068);
  FUN_01018280(lVar1 + 0x8c);
  *(undefined8 *)(lVar1 + 0x118) = 0;
  *(undefined8 *)(lVar1 + 0x120) = 0xffffffffffffffff;
  *(undefined4 *)(lVar1 + 0x128) = 0xffffffff;
  *(undefined1 *)(lVar1 + 300) = 1;
  cVar2 = FUN_00752150(0);
  if ((cVar2 == '\0') && (cVar2 = FUN_00752150(1), cVar2 == '\0')) {
    return;
  }
  *(undefined1 *)(lVar1 + 300) = 0;
  return;
}

