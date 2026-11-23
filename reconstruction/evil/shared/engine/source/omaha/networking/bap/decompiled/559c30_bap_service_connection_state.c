
byte FUN_00559c30(int param_1)

{
  char cVar1;
  byte bVar2;
  long lVar3;
  
  bVar2 = 0;
  if (*(int *)(DAT_026b9968 + 8 + (long)param_1 * 0x18) != -1) {
    lVar3 = FUN_00b333a0();
    bVar2 = 0;
    if (lVar3 != 0) {
      cVar1 = FUN_00b2e830(lVar3);
      bVar2 = 1;
      if (cVar1 == '\0') {
        cVar1 = FUN_00b2e840(lVar3);
        bVar2 = 3;
        if (cVar1 == '\0') {
          cVar1 = FUN_00b2e850(lVar3);
          bVar2 = 2;
          if (cVar1 == '\0') {
            bVar2 = FUN_00b2d6a0(lVar3);
            bVar2 = bVar2 | 4;
          }
        }
      }
    }
  }
  return bVar2;
}

