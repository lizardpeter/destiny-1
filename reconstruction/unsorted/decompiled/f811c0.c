
void FUN_00f811c0(long param_1,undefined4 param_2,undefined4 param_3)

{
  char cVar1;
  long lVar2;
  
  lVar2 = *(long *)(param_1 + 0x10);
  if ((uint)((ulong)(*(long *)(param_1 + 8) - lVar2) >> 2) < 7) {
    cVar1 = (**(code **)(param_1 + 0x18))(param_1,7,*(undefined8 *)(param_1 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    lVar2 = *(long *)(param_1 + 0x10);
  }
  thunk_FUN_012ac5e6(lVar2,7,param_2,param_3);
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + 0x1c;
  return;
}

