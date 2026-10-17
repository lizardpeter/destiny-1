
undefined4 FUN_00264310(undefined4 param_1)

{
  long *plVar1;
  long lVar2;
  undefined4 uVar3;
  
  plVar1 = (long *)FUN_0025cbd0();
  lVar2 = (**(code **)(*plVar1 + 800))(plVar1,param_1);
  uVar3 = 0xffffffff;
  if (*(long *)(lVar2 + 0x20) != 0) {
    uVar3 = *(undefined4 *)(*(long *)(lVar2 + 0x20) + 0x2c + lVar2);
  }
  return uVar3;
}

