
ulong FUN_0010cb60(int *param_1,int *param_2)

{
  int iVar1;
  long lVar2;
  char cVar3;
  ulong uVar4;
  long lVar5;
  long lVar6;
  uint local_40 [2];
  long local_38;
  ulong local_28;
  
  local_28 = *DAT_01a1f100;
  cVar3 = FUN_001072c0(0x10,0,local_40);
  if ((cVar3 == '\0') || (local_40[0] == 0xffffffff)) {
    FUN_000a0760(param_1);
    *param_2 = -0x7ee3623b;
  }
  else {
    lVar5 = (ulong)(((uint)((int)local_40[0] >> 0xd) >> 0x12 | 0x3ff) & (int)local_40[0] >> 0xd) *
            0x40;
    lVar6 = *DAT_01a238a0;
    lVar2 = *(long *)(lVar6 + 0x10 + lVar5);
    uVar4 = (ulong)((local_40[0] & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar5));
    lVar6 = (lVar2 + uVar4) - ((long)*(int *)(lVar6 + 0x34 + lVar5) & *(ulong *)(lVar2 + 8 + uVar4))
    ;
    *param_1 = *(int *)(local_38 + 0x674 + lVar6);
    iVar1 = *(int *)(local_38 + 0x678 + lVar6);
    *param_2 = iVar1;
    if (iVar1 != -0x7ee3623b) {
      if (*DAT_01a1f100 == local_28) {
        return (ulong)CONCAT31((int3)((uint)iVar1 >> 8),*param_1 != -1);
      }
      goto LAB_0010cc4e;
    }
  }
  if (*DAT_01a1f100 == local_28) {
    return *DAT_01a1f100 & 0xffffffffffffff00;
  }
LAB_0010cc4e:
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

