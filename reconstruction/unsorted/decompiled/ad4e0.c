
void FUN_000ad4e0(void)

{
  long lVar1;
  
  lVar1 = (long)DAT_01ad4840 * 0x3b0;
  if ((&DAT_01ad40e0)[lVar1] != '\0') {
    *(undefined8 *)(&DAT_01ad43f0 + lVar1) = 0;
    *(undefined8 *)(lVar1 + 0x1ad43f8) = 0;
  }
  lVar1 = (long)DAT_01ad4840 * 0x3b0;
  if ((&DAT_01ad40e1)[lVar1] != '\0') {
    *(undefined8 *)(&DAT_01ad4400 + lVar1) = 0;
    *(undefined8 *)(lVar1 + 0x1ad4408) = 0;
  }
  lVar1 = (long)DAT_01ad4840 * 0x3b0;
  if ((&DAT_01ad40e2)[lVar1] != '\0') {
    *(undefined8 *)(&DAT_01ad4410 + lVar1) = 0;
    *(undefined8 *)(lVar1 + 0x1ad4418) = 0;
  }
  lVar1 = (long)DAT_01ad4840 * 0x3b0;
  if ((&DAT_01ad40e3)[lVar1] != '\0') {
    *(undefined8 *)(&DAT_01ad4420 + lVar1) = 0;
    *(undefined8 *)(lVar1 + 0x1ad4428) = 0;
  }
  FUN_000ae260(0,4,&DAT_01ad40e0 + (long)DAT_01ad4840 * 0x3b0,
               &DAT_01ad43f0 + (long)DAT_01ad4840 * 0x3b0);
  return;
}

