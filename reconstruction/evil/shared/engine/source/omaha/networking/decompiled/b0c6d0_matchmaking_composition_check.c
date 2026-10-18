
int FUN_00b0c6d0(long param_1,long *param_2)

{
  bool bVar1;
  byte bVar2;
  int iVar3;
  int iVar4;
  bool bVar5;
  
  iVar4 = 3;
  if ((param_1 == 0) || (param_2 == (long *)0x0)) goto LAB_00b0c7e3;
  iVar4 = 1;
  if ((*(byte *)((long)param_2 + 0x1b9) & 2) != 0) goto LAB_00b0c7e3;
  bVar2 = *(byte *)((long)param_2 + 0x1b9) & 1;
  iVar4 = (uint)(bVar2 == 0) * 2;
  if (bVar2 == 0) {
LAB_00b0c727:
    if (iVar4 != 0) goto LAB_00b0c7e3;
  }
  else if (*(int *)(param_1 + 0x28) != -1) {
    if (*(int *)((long)param_2 + 0xc) == -1) {
      iVar4 = 4;
    }
    goto LAB_00b0c727;
  }
  if ((*(int *)(param_1 + 0x28) != -1) ||
     (bVar5 = *(int *)((long)param_2 + 0xc) == -1, bVar1 = !bVar5, bVar5)) {
    iVar4 = 6;
    if (*(long *)(param_1 + 0x30) == *param_2) {
      iVar4 = 0;
      if (*(int *)(param_1 + 4) != (int)param_2[1]) {
        iVar4 = 7;
      }
      if (iVar4 == 0) {
        bVar2 = FUN_000d2e50(param_1 + 0x28,(long)param_2 + 0xc);
        if (bVar2 == 0) {
          iVar3 = *(int *)(param_1 + 0x9c);
          iVar4 = (int)param_2[5];
          if (iVar3 < iVar4) {
            iVar4 = (uint)(iVar3 < iVar4) + (uint)(iVar3 < iVar4) * 8;
          }
          else {
            iVar4 = 0xb;
            if (*(int *)((long)param_2 + 0x16c) <= *(int *)(param_1 + 0xa0)) {
              if (iVar3 < (int)param_2[0x33]) {
                iVar4 = 10;
              }
              else {
                iVar4 = 0xc;
                if (*(int *)((long)param_2 + 0x14) <= *(int *)(param_1 + 0xc4)) {
                  iVar4 = 0;
                }
              }
            }
          }
        }
        else {
          iVar4 = (uint)bVar2 << 3;
        }
      }
    }
  }
  else {
    iVar4 = (uint)bVar1 + (uint)bVar1 * 4;
  }
LAB_00b0c7e3:
  iVar3 = 0x12;
  if (iVar4 != 0) {
    iVar3 = iVar4;
  }
  return iVar3;
}

