
void FUN_00f7fa20(long param_1,undefined8 param_2,undefined4 *param_3)

{
  char cVar1;
  int iVar2;
  long lVar3;
  
  lVar3 = *(long *)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - lVar3) >> 2) < 0x1e) {
    cVar1 = (**(code **)(param_1 + 0x18))(param_1,0x1e,*(undefined8 *)(param_1 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    lVar3 = *(long *)(param_1 + 0x10);
  }
  iVar2 = thunk_FUN_012ac5a6(lVar3,0x1e,param_2,*param_3);
  if (iVar2 == 0) {
    *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0x78;
  }
  return;
}

