
bool FUN_002680a0(undefined4 param_1,undefined4 param_2,char param_3)

{
  long lVar1;
  int iVar2;
  long *plVar3;
  bool bVar4;
  
  bVar4 = true;
  if (param_3 == '\0') {
    plVar3 = (long *)FUN_0025a550();
    lVar1 = (**(code **)(*plVar3 + 0x328))(plVar3,param_2);
    iVar2 = FUN_00267090(param_1,*(undefined4 *)(lVar1 + 0x8c));
    bVar4 = iVar2 != 7;
  }
  return bVar4;
}

