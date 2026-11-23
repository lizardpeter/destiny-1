
undefined1 FUN_0057ce50(long *param_1)

{
  int iVar1;
  long *plVar2;
  long lVar3;
  long *plVar4;
  undefined1 uVar5;
  
  uVar5 = 0;
  if (param_1[1] == *param_1) {
    plVar4 = param_1 + 0x2a;
    uVar5 = 1;
    lVar3 = 0x18;
    do {
      if ((*(byte *)((long)param_1 + lVar3) & 4) != 0) {
        plVar2 = (long *)FUN_00057f80(plVar4);
        if (*plVar2 != 0) {
          iVar1 = FUN_010150a0(plVar4);
          if (iVar1 != 2) {
            uVar5 = 0;
          }
        }
      }
      plVar4 = plVar4 + 3;
      lVar3 = lVar3 + 0x10;
    } while ((int)lVar3 != 0x158);
  }
  return uVar5;
}

