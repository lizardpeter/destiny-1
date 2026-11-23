
int FUN_00264360(undefined8 param_1,long param_2)

{
  long lVar1;
  long lVar2;
  char cVar3;
  long *plVar4;
  long lVar5;
  long lVar6;
  
  plVar4 = (long *)(param_2 + 0x20);
  lVar5 = *(long *)(param_2 + 0x18) + 1;
  lVar1 = *(long *)(param_2 + 0x18) * 0x18;
  do {
    lVar6 = lVar1;
    lVar5 = lVar5 + -1;
    if (lVar5 < 1) {
      return 0;
    }
    lVar2 = *plVar4;
    lVar1 = (long)plVar4 + lVar6 + lVar2;
    cVar3 = FUN_0028eba0(lVar1);
    if (cVar3 == '\0') break;
    cVar3 = FUN_0028e530(param_1,lVar1);
    lVar1 = lVar6 + -0x18;
  } while (cVar3 == '\0');
  return (int)*(char *)((long)plVar4 + lVar6 + lVar2 + -8);
}

