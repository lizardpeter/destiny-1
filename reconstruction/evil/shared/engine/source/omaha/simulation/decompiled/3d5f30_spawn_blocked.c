
byte FUN_003d5f30(void)

{
  byte bVar1;
  long lVar2;
  long lVar3;
  
  lVar2 = FUN_007642e0();
  lVar3 = 0;
  if (lVar2 != 0) {
    lVar3 = FUN_002a2d40(lVar2);
    lVar3 = lVar3 + 0x5010;
  }
  lVar2 = FUN_007642e0();
  bVar1 = 0;
  if ((lVar3 != 0) && (lVar2 != 0)) {
    bVar1 = FUN_0010ba00(lVar3);
    bVar1 = *(char *)(lVar2 + 0x1c) != '\0' | bVar1 ^ 1;
  }
  return bVar1;
}

