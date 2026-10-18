
void FUN_0090cee0(void)

{
  long *plVar1;
  char cVar2;
  long lVar3;
  undefined1 local_40 [16];
  long local_30;
  
  plVar1 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  if (*(int *)(DAT_0273ea98 + 4) != -1) {
    FUN_0063fc10();
    *(undefined4 *)(DAT_0273ea98 + 4) = 0xffffffff;
  }
  FUN_00074a80(local_40,DAT_0273ea80);
  while( true ) {
    lVar3 = FUN_00074a90(local_40);
    if (lVar3 == 0) break;
    FUN_0090cfc0(lVar3);
    FUN_0063fce0(*(undefined4 *)(lVar3 + 0x2858));
    *(undefined4 *)(lVar3 + 0x2858) = 0xffffffff;
  }
  cVar2 = FUN_0092c710();
  if (cVar2 != '\0') {
    cVar2 = FUN_0092c720();
    if (cVar2 != '\0') goto LAB_0090cfa1;
  }
  FUN_00074740(DAT_0273ea80);
  *DAT_0273ea90 = 0;
  FUN_00922e00();
LAB_0090cfa1:
  if (*plVar1 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

