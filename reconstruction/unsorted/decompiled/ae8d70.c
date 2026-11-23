
void FUN_00ae8d70(void)

{
  long lVar1;
  undefined4 uVar2;
  undefined8 uVar3;
  undefined1 auVar4 [16];
  
  lVar1 = DAT_027be860;
  uVar3 = FUN_003430b0();
  uVar2 = FUN_00345620(uVar3);
  *(undefined4 *)(lVar1 + 4) = uVar2;
  uVar3 = FUN_003430b0();
  uVar2 = FUN_00345610(uVar3);
  *(undefined4 *)(lVar1 + 8) = uVar2;
  uVar3 = FUN_003430b0();
  auVar4 = FUN_003457a0(uVar3);
  *(undefined1 (*) [16])(lVar1 + 0xc) = auVar4;
  uVar3 = FUN_003430b0();
  uVar2 = FUN_00345a80(uVar3);
  *(undefined4 *)(lVar1 + 0x1c) = uVar2;
  return;
}

