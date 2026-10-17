
void FUN_00263c20(undefined8 *param_1)

{
  char cVar1;
  int iVar2;
  long lVar3;
  
  *(undefined4 *)(param_1 + 2) = 0xffffffff;
  cVar1 = (**(code **)(*(long *)*param_1 + 0x58))();
  if ((cVar1 != '\0') &&
     (lVar3 = (**(code **)(*(long *)*param_1 + 0x10))(), *(char *)(lVar3 + 0x714c) != '\0')) {
    *(int *)(param_1 + 2) = *(int *)(param_1 + 2) + 1;
    return;
  }
  while( true ) {
    iVar2 = *(int *)(param_1 + 2) + 1;
    *(int *)(param_1 + 2) = iVar2;
    lVar3 = param_1[1];
    if ((ulong)(long)*(int *)(lVar3 + 8) <= (ulong)(long)iVar2) {
      return;
    }
    lVar3 = *(long *)(lVar3 + 0x10) + lVar3 + 0x28 + (long)iVar2 * 0x18;
    cVar1 = FUN_0028eba0(lVar3);
    if (cVar1 == '\0') break;
    cVar1 = FUN_0028e530(*param_1,lVar3);
    if (cVar1 != '\0') {
      return;
    }
  }
  return;
}

