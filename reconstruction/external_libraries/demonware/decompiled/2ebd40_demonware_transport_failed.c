
undefined4 FUN_002ebd40(void)

{
  code *pcVar1;
  char cVar2;
  int iVar3;
  long *plVar4;
  undefined8 uVar5;
  undefined1 *puVar6;
  
  puVar6 = &stack0xffffffffffffffe8;
  if (DAT_02f66f68 == (long *)0x0) {
    plVar4 = (long *)FUN_01224590(0x5120);
    FUN_012395f0(plVar4);
    DAT_02f66f68 = plVar4;
    if (plVar4 == (long *)0x0) {
      pcVar1 = (code *)swi(0x41);
      (*pcVar1)();
      puVar6 = &stack0xfffffffffffffff0;
    }
    else {
      uVar5 = FUN_01019d10();
      cVar2 = FUN_01019da0(uVar5,FUN_01019e60);
      puVar6 = &stack0xffffffffffffffe8;
      if (cVar2 == '\0') {
        if (DAT_02f66f68 != (long *)0x0) {
          (**(code **)(*DAT_02f66f68 + 8))();
        }
        DAT_02f66f68 = (long *)0x0;
        pcVar1 = (code *)swi(0x41);
        (*pcVar1)();
        puVar6 = &stack0xfffffffffffffff0;
      }
    }
  }
  *(undefined8 *)(puVar6 + -8) = 0x2ebdac;
  iVar3 = FUN_01239520(DAT_02f66f68);
  return CONCAT31((int3)(iVar3 - 1U >> 8),1 < iVar3 - 1U);
}

