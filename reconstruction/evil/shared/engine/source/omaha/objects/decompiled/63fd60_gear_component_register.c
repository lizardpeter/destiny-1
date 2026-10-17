
void FUN_0063fd60(undefined4 param_1,undefined4 param_2)

{
  long lVar1;
  uint uVar2;
  ulong uVar3;
  
  uVar2 = FUN_0006e750(&DAT_026beab0);
  lVar1 = DAT_026beab8;
  if (uVar2 != 0xffffffff) {
    uVar3 = (ulong)((uVar2 & 0x1fff) * DAT_026beac0);
    *(undefined4 *)(DAT_026beab8 + uVar3) = param_1;
    *(undefined4 *)(lVar1 + 4 + uVar3) = param_2;
  }
  return;
}

