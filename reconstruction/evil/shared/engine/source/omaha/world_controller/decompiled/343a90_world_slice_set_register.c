
undefined8 FUN_00343a90(long param_1,undefined4 param_2,int param_3,long param_4)

{
  int *piVar1;
  long lVar2;
  int iVar3;
  long lVar4;
  undefined8 uVar5;
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar2 = *(long *)(param_1 + 8);
  local_40[0] = param_2;
  iVar3 = FUN_00057e60(local_40);
  lVar4 = (long)iVar3 * 0x10;
  piVar1 = (int *)(lVar2 + 0x10 + lVar4);
  if ((*(int *)(lVar2 + 0x10 + lVar4) != param_3) || (*(long *)(lVar2 + 0x18 + lVar4) != param_4)) {
    if (param_3 != -1) {
      iVar3 = FUN_0012d700(local_40);
      *piVar1 = param_3;
      *(long *)(lVar2 + 0x18 + lVar4) = param_4;
      if (*DAT_01a1f100 == local_38) {
        return CONCAT71((int7)(int3)((uint)iVar3 >> 8),
                        *(int *)(lVar2 + 0x2014 + (long)iVar3 * 4) != -1);
      }
      goto LAB_00343b80;
    }
    piVar1[2] = 0;
    piVar1[3] = 0;
    piVar1[0] = 0;
    piVar1[1] = 0;
    *piVar1 = -1;
    FUN_0012d790(lVar2 + 0x215c,local_40[0],0);
    FUN_0012d790(lVar2 + 0x219c,local_40[0],0);
  }
  if (*DAT_01a1f100 == local_38) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
  }
LAB_00343b80:
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

