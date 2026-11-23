
void FUN_00585800(undefined8 param_1,char *param_2)

{
  char cVar1;
  long lVar2;
  undefined8 *puVar3;
  
  puVar3 = (undefined8 *)0x0;
  lVar2 = 0;
  if (DAT_026bc4e0 != 0) {
    lVar2 = DAT_026bc4e0;
  }
  cVar1 = *param_2;
  if (cVar1 == '\x02') {
    puVar3 = (undefined8 *)(lVar2 + 0x54);
  }
  else if (cVar1 == '\x01') {
    puVar3 = (undefined8 *)(lVar2 + 0x4c);
  }
  else if (cVar1 == '\0') {
    puVar3 = (undefined8 *)(lVar2 + 0x44);
  }
  *puVar3 = 0xffffffffffffffff;
  return;
}

