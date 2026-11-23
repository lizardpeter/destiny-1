
void FUN_00267b50(long *param_1,undefined4 param_2)

{
  char cVar1;
  undefined8 uVar2;
  long lVar3;
  long lVar4;
  bool bVar5;
  
  uVar2 = (**(code **)(*param_1 + 0x18))();
  lVar3 = FUN_002601f0(param_1);
  cVar1 = (**(code **)(*param_1 + 0x58))(param_1);
  bVar5 = false;
  if (cVar1 != '\0') {
    lVar4 = (**(code **)(*param_1 + 0x10))(param_1);
    bVar5 = *(char *)(lVar4 + 0x714c) != '\0';
  }
  FUN_002679e0(uVar2,lVar3 + 4,param_2,bVar5);
  return;
}

