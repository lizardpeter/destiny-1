
undefined8 FUN_00fa7e10(long param_1)

{
  undefined8 uVar1;
  char *pcVar2;
  long lVar3;
  
  uVar1 = thunk_FUN_012ac976(FUN_00fa7ee0,param_1,param_1 + 0x54);
  if ((int)uVar1 == 0) {
    FUN_00fbdbd0(DAT_029589a0,5,0,0,0);
    pcVar2 = (char *)FUN_00fbd780(*(long *)(*(long *)(param_1 + 8) + 0xa8) + 0x48);
    if (*pcVar2 != '\0') {
      uVar1 = FUN_00fbd780(*(long *)(*(long *)(param_1 + 8) + 0xa8) + 0x48);
      lVar3 = FUN_00fbd780(*(long *)(*(long *)(param_1 + 8) + 0xa8) + 0x48);
      thunk_FUN_012ab8d6(uVar1,lVar3 + 0x10);
    }
    uVar1 = thunk_FUN_012ac986(FUN_00fa7f80,param_1);
    if ((int)uVar1 == 0) {
      uVar1 = FUN_00fbc180(param_1 + 0x68);
      if ((int)uVar1 == 0) {
        FUN_00f97230(*(undefined8 *)(param_1 + 8),1);
        uVar1 = 0;
      }
    }
  }
  return uVar1;
}

