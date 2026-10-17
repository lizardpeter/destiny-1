
long FUN_0057de80(long param_1)

{
  long lVar1;
  long lVar2;
  long lVar3;
  
  lVar3 = *DAT_01a1f100;
  lVar1 = FUN_00557c40(&DAT_026bc508);
  lVar2 = 0;
  if (lVar1 != 0) {
    lVar1 = FUN_005863c0(lVar1);
    if (((lVar1 != 0) && (lVar1 == param_1)) && (lVar2 = 0, DAT_026bc410 != 0)) {
      lVar2 = DAT_026bc410 + 0x40;
    }
  }
  if (*DAT_01a1f100 == lVar3) {
    return lVar2;
  }
  lVar3 = thunk_FUN_012aa7f6();
  return lVar3;
}

