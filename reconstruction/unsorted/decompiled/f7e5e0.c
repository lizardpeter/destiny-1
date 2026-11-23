
void FUN_00f7e5e0(long param_1)

{
  char cVar1;
  uint uVar2;
  long lVar3;
  long lVar4;
  
  lVar3 = *(long *)(param_1 + 8);
  lVar4 = *(long *)(param_1 + 0x10);
  if ((uint)((ulong)(lVar3 - lVar4) >> 2) < 0x100) {
    cVar1 = (**(code **)(param_1 + 0x18))(param_1,0x100,*(undefined8 *)(param_1 + 0x20));
    if (cVar1 == '\0') {
      return;
    }
    lVar3 = *(long *)(param_1 + 8);
    lVar4 = *(long *)(param_1 + 0x10);
  }
  uVar2 = thunk_FUN_012ac566(lVar4,(ulong)(lVar3 - lVar4) >> 2);
  *(long *)(param_1 + 0x10) = *(long *)(param_1 + 0x10) + (ulong)uVar2 * 4;
  return;
}

