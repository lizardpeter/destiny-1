
undefined2 FUN_00264980(undefined8 param_1)

{
  long lVar1;
  long lVar2;
  char cVar3;
  long *plVar4;
  long lVar5;
  long lVar6;
  long lVar7;
  
  plVar4 = (long *)FUN_0025a550();
  lVar5 = (**(code **)(*plVar4 + 0x28))(plVar4);
  lVar6 = -1;
  plVar4 = (long *)(lVar5 + 0x20);
  lVar1 = 0x18;
  do {
    lVar7 = lVar1;
    lVar6 = lVar6 + 1;
    if (*(long *)(lVar5 + 0x18) <= lVar6) {
      return 0xffff;
    }
    lVar2 = *plVar4;
    lVar1 = (long)plVar4 + lVar7 + lVar2;
    cVar3 = FUN_0028eba0(lVar1);
    if (cVar3 == '\0') break;
    cVar3 = FUN_0028e530(param_1,lVar1);
    lVar1 = lVar7 + 0x18;
  } while (cVar3 == '\0');
  return *(undefined2 *)((long)plVar4 + lVar7 + lVar2 + -8);
}

