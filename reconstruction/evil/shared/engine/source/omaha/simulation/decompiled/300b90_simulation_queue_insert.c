
void FUN_00300b90(char *param_1)

{
  char cVar1;
  long lVar2;
  
  lVar2 = DAT_02689540;
  cVar1 = FUN_00240e60();
  if (cVar1 != '\0') {
    return;
  }
  cVar1 = FUN_002ffe70((int)*param_1);
  if (cVar1 == '\0') {
    lVar2 = lVar2 + 0x28;
  }
  FUN_002ff6e0(lVar2,param_1);
  return;
}

