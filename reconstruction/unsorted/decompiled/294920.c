
void FUN_00294920(undefined4 param_1)

{
  uint uVar1;
  uint uVar2;
  ulong uVar3;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_40 = 0;
  if (DAT_026534e0 != 0) {
    uVar3 = 0;
    uVar1 = DAT_026534e0;
    do {
      if (((&DAT_026532b0)[uVar3 * 3] & 1L << ((byte)param_1 & 0x3f)) != 0) {
        (*(code *)(&DAT_026532a0)[uVar3 * 3])((&DAT_026532a8)[uVar3 * 3],param_1,&local_40);
        uVar1 = DAT_026534e0;
      }
      uVar2 = (int)uVar3 + 1;
      uVar3 = (ulong)uVar2;
    } while (uVar2 < uVar1);
  }
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

