
char FUN_007a2d60(void)

{
  long lVar1;
  char cVar2;
  char cVar3;
  long lVar4;
  undefined8 uVar5;
  
  cVar2 = FUN_007724f0(0);
  cVar3 = '\x02';
  if (cVar2 != '\0') {
    cVar2 = FUN_007754d0(0);
    lVar4 = FUN_00775770(0);
    if (cVar2 == '\0') {
      cVar2 = FUN_007855c0(0);
      if (cVar2 == '\0') {
        lVar1 = lVar4 + 0x9b8;
        cVar2 = FUN_00b8f690(lVar1);
        if ((cVar2 != '\0') && (cVar2 = FUN_00b8e250(lVar1), cVar2 == '\0')) {
          return '\x01';
        }
        cVar2 = FUN_00b8f690(lVar4 + 0x390);
        if ((cVar2 != '\0') && (cVar2 = FUN_00b8e250(lVar1), cVar2 == '\0')) {
          return '\x01';
        }
        cVar2 = FUN_00b8f690(lVar4 + 0x1678);
        cVar3 = (cVar2 == '\0') + '\x01';
      }
    }
    else {
      FUN_00b8e0b0(lVar4 + 0x9b8);
      FUN_00b8efe0(lVar4 + 0x390);
      FUN_00b8c940(lVar4,0x12);
      uVar5 = FUN_00574ef0();
      FUN_00574bc0(uVar5);
    }
  }
  return cVar3;
}

