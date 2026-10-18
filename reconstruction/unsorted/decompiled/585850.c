
void FUN_00585850(undefined8 param_1,char *param_2)

{
  char cVar1;
  long lVar2;
  
  lVar2 = 0;
  if (DAT_026bc4e0 != 0) {
    lVar2 = DAT_026bc4e0;
  }
  cVar1 = *param_2;
  if ((*(char *)(lVar2 + 0x40) != cVar1) && (*(char *)(lVar2 + 0x40) = cVar1, cVar1 == '\x04')) {
    FUN_00585030(lVar2,1);
    cVar1 = *(char *)(lVar2 + 0x40);
  }
  if ((int)cVar1 - 7U < 6) {
    cVar1 = param_2[1];
    if (cVar1 != *(char *)(lVar2 + 0x41)) {
      if ((*(char *)(lVar2 + 0x41) < '\x03') && ('\x02' < cVar1)) {
        FUN_00585030(lVar2,0);
        cVar1 = param_2[1];
      }
      *(char *)(lVar2 + 0x41) = cVar1;
    }
  }
  return;
}

