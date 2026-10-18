
/* WARNING: Globals starting with '_' overlap smaller symbols at the same address */

undefined4 FUN_007e3860(int *param_1)

{
  int iVar1;
  int iVar2;
  undefined1 uVar3;
  long *in_FS_OFFSET;
  
  iVar1 = *param_1;
  uVar3 = 0;
  if (iVar1 != 0) {
    uVar3 = FUN_007e5330(param_1 + 4);
    *(undefined8 *)(*in_FS_OFFSET + _DAT_01a1f4c8) = 0;
    do {
      iVar2 = *param_1;
      LOCK();
      iVar1 = *param_1;
      if (iVar2 == iVar1) {
        *param_1 = 0;
        iVar1 = iVar2;
      }
      UNLOCK();
    } while (iVar2 != iVar1);
  }
  return CONCAT31((int3)((uint)iVar1 >> 8),uVar3);
}

