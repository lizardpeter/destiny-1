
void FUN_00672b60(undefined4 *param_1,undefined4 param_2,undefined4 *param_3,uint param_4,
                 undefined4 *param_5)

{
  uint uVar1;
  long lVar2;
  undefined4 local_60 [2];
  undefined1 local_58 [24];
  byte local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_00643fa0(param_5);
  if (param_4 == 3) {
    lVar2 = 0;
    do {
      param_5[lVar2 + 0xe] = param_1[lVar2];
      param_5[lVar2 * 2] = param_1[10];
      param_5[lVar2 * 2 + 1] = param_1[0xb];
      lVar2 = lVar2 + 1;
    } while ((int)lVar2 != 7);
  }
  else {
    param_5[0xe] = *param_1;
    *param_5 = param_1[10];
    param_5[1] = param_1[0xb];
    param_5[0xf] = param_1[1];
    param_5[2] = param_1[10];
    param_5[3] = param_1[0xb];
    param_5[0x10] = param_1[2];
    param_5[4] = param_1[10];
    param_5[5] = param_1[0xb];
    param_5[0x11] = param_1[3];
    param_5[6] = param_1[10];
    param_5[7] = param_1[0xb];
    param_5[0x12] = param_1[4];
    param_5[8] = param_1[10];
    param_5[9] = param_1[0xb];
    param_5[0x13] = param_1[5];
    param_5[10] = param_1[10];
    param_5[0xb] = param_1[0xb];
    param_5[0xc] = param_1[10];
    param_5[0xd] = param_1[0xb];
  }
  param_5[0x15] = param_1[7];
  param_5[0x16] = param_1[8];
  param_5[0x17] = param_1[9];
  FUN_00640c10(local_58);
  if (param_4 == 3) {
    uVar1 = local_40 ^ 1;
  }
  else {
    uVar1 = 0;
    if (param_4 < 3) {
      uVar1 = 2;
    }
  }
  param_5[0x18] = uVar1;
  local_60[0] = *param_3;
  FUN_00672cf0(param_2,local_60,param_5 + 0x19,param_5 + 0x1a);
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

