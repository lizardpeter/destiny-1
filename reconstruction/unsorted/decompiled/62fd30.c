
undefined8 FUN_0062fd30(long param_1,int *param_2)

{
  int *piVar1;
  long lVar2;
  undefined8 uVar3;
  int local_28 [2];
  undefined8 local_20;
  long local_18;
  
  local_18 = *DAT_01a1f100;
  if (*param_2 != 0) {
    local_20 = *(undefined8 *)(param_2 + 2);
    local_28[0] = *param_2;
    lVar2 = FUN_00078970(local_28,*(undefined4 *)PTR_DAT_019b3ed0);
    if (lVar2 != 0) {
      *(float *)(param_1 + 0x300) = *(float *)(lVar2 + 0x14) + *(float *)(param_1 + 0x300);
      if (0.0 <= *(float *)(lVar2 + 0xc)) {
        *(float *)(param_1 + 0x2fc) = *(float *)(lVar2 + 0xc);
      }
      if (*(int *)(lVar2 + 0x10) != -1) {
        *(int *)(param_1 + 0x2f8) = *(int *)(lVar2 + 0x10);
      }
    }
  }
  piVar1 = (int *)(DAT_026be8a0 + (long)*(int *)(param_1 + 0x2f8) * 4);
  *piVar1 = *piVar1 + 1;
  if (*DAT_01a1f100 == local_18) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

