
void FUN_0056e280(int param_1,undefined8 param_2,char *param_3)

{
  long *plVar1;
  int iVar2;
  undefined1 local_b0 [4];
  uint auStack_ac [33];
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  FUN_0056e330();
  if ((param_1 == 4) && (*param_3 != '\0')) {
    FUN_0056fda0(4,local_b0);
    iVar2 = 0;
    do {
      if (((*(uint *)(param_3 + (long)(iVar2 >> 5) * 4 + 4) >> ((byte)iVar2 & 0x1f) & 1) == 0) &&
         ((auStack_ac[iVar2 >> 5] & 1 << ((byte)iVar2 & 0x1f)) != 0)) {
        FUN_00ac1ae0(iVar2);
      }
      iVar2 = iVar2 + 1;
    } while ((short)iVar2 != 0x400);
  }
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

