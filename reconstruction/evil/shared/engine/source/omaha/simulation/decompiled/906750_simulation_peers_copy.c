
void FUN_00906750(void)

{
  long lVar1;
  char cVar2;
  int iVar3;
  long lVar4;
  char *pcVar5;
  
  cVar2 = FUN_0092c710();
  if (cVar2 != '\0') {
    cVar2 = FUN_0092c720();
    if (cVar2 != '\0') {
      return;
    }
  }
  lVar1 = DAT_0273dcd0;
  FUN_00913a90(*(undefined4 *)(DAT_0273dcd0 + 0x20),DAT_0273dcd0 + 0x24);
  if (*(char *)(lVar1 + 0xc4) == '\0') {
    lVar4 = 0;
  }
  else {
    lVar4 = lVar1 + 0xc5;
  }
  FUN_00913d20(lVar4);
  pcVar5 = (char *)(lVar1 + 0xd0);
  iVar3 = 0;
  do {
    if (*pcVar5 != '\0') {
      FUN_0090ee70(iVar3,pcVar5,0);
    }
    pcVar5 = pcVar5 + 0xe8;
    iVar3 = iVar3 + 1;
  } while (iVar3 != 0x14);
  FUN_0090fbe0();
  FUN_00b9f270();
  return;
}

