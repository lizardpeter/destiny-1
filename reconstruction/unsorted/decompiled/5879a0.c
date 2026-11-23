
void FUN_005879a0(undefined8 param_1,undefined8 *param_2)

{
  long lVar1;
  undefined4 uVar2;
  
  lVar1 = DAT_026bc510;
  if (DAT_026bc510 != 0) {
    uVar2 = FUN_005916f0();
    *(undefined4 *)(lVar1 + 0x418) = uVar2;
    *(undefined8 *)(lVar1 + 0x408) = *param_2;
    *(undefined8 *)(lVar1 + 0x410) = param_2[1];
  }
  return;
}

