
long FUN_0056dc00(long param_1,int param_2,int param_3,long *param_4)

{
  long lVar1;
  ulong uVar2;
  long *plVar3;
  long lVar4;
  long lVar5;
  int iVar6;
  long lVar7;
  
  lVar5 = (long)param_2 * 0x60 + param_1;
  lVar7 = (long)param_3 * 0x10;
  uVar2 = (ulong)*(uint *)(lVar7 + 0x4fd90 + lVar5);
  if (uVar2 == 0xffffffff) {
    return 0;
  }
  lVar4 = (long)*(int *)(lVar7 + 0x4fd98 + lVar5);
  plVar3 = (long *)(param_1 + 0x40a0 + uVar2);
  iVar6 = -1;
  do {
    iVar6 = iVar6 + 1;
    if (*(short *)(lVar7 + 0x4fd94 + lVar5) <= iVar6) {
      return 0;
    }
    lVar1 = *plVar3;
    plVar3 = (long *)((long)plVar3 + lVar4);
  } while (lVar1 != *param_4);
  return (long)plVar3 - lVar4;
}

