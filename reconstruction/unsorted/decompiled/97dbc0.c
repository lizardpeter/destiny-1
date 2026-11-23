
undefined8 FUN_0097dbc0(long param_1,undefined8 *param_2,long *param_3)

{
  int iVar1;
  long lVar2;
  long lVar3;
  
  lVar3 = 1;
  if (1 < *(short *)*param_2) {
    lVar2 = FUN_0097e560(*(undefined8 *)(param_1 + 0x90));
    lVar3 = 0;
    if (lVar2 != 0) {
      lVar3 = 1;
      if (*(code **)(lVar2 + 0x38) != (code *)0x0) {
        iVar1 = (**(code **)(lVar2 + 0x38))(param_1);
        lVar3 = (long)iVar1;
      }
    }
  }
  *param_3 = lVar3;
  return 1;
}

