
void FUN_00585a80(undefined8 param_1)

{
  char cVar1;
  undefined8 uVar2;
  
  cVar1 = FUN_0012f640();
  if (cVar1 == '\0') {
    FUN_00543f70(param_1,1000);
  }
  FUN_00544000(param_1);
  cVar1 = FUN_0010b400(param_1);
  if (cVar1 != '\0') {
    cVar1 = FUN_002f1a30();
    if (cVar1 == '\0') {
      uVar2 = 1000;
    }
    else {
      uVar2 = 60000;
    }
    FUN_00543f70(param_1,uVar2);
    return;
  }
  return;
}

