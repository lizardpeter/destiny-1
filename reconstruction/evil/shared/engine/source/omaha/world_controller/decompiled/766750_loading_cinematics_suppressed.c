
byte FUN_00766750(void)

{
  char cVar1;
  char *pcVar2;
  byte bVar3;
  
  pcVar2 = (char *)FUN_00574ef0();
  cVar1 = *pcVar2;
  bVar3 = FUN_0078c710();
  return bVar3 | cVar1 == '\x01';
}

