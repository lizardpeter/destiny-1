
undefined8
FUN_0006c620(long param_1,undefined8 param_2,int param_3,undefined8 param_4,undefined8 param_5)

{
  int iVar1;
  undefined8 uVar2;
  bool bVar3;
  undefined1 local_1158 [4392];
  long local_30;
  
  local_30 = *DAT_01a1f100;
  iVar1 = FUN_00f6c810(*(undefined4 *)(param_1 + 4),param_4,param_1 + 0x10,
                       *(undefined4 *)(param_1 + 8),0,local_1158);
  bVar3 = false;
  if (iVar1 == 0) {
    iVar1 = FUN_00f6c430(param_2,param_5,(long)param_3,local_1158);
    if (iVar1 == 0) {
      iVar1 = FUN_00f6c5f0(local_1158);
      bVar3 = iVar1 == 0;
    }
  }
  if (*DAT_01a1f100 == local_30) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),bVar3);
  }
  uVar2 = thunk_FUN_012aa7f6();
  return uVar2;
}

