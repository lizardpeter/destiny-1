
void FUN_00106d60(long param_1,undefined4 param_2)

{
  undefined8 uVar1;
  undefined4 local_20;
  undefined4 uStack_1c;
  undefined4 local_18 [2];
  long local_10;
  
  local_10 = *DAT_01a1f100;
  _local_20 = CONCAT44(*(undefined4 *)(param_1 + 0x28),param_2);
  local_18[0] = *(undefined4 *)(param_1 + 0xc);
  uVar1 = 0;
  if ((ulong)DAT_025d6ff8 != 0) {
    uVar1 = *(undefined8 *)(&DAT_01ad5030 + (ulong)DAT_025d6ff8 * DAT_01ad5010 + DAT_01ad5000);
  }
  FUN_0100d5e0(uVar1,local_18,param_1 + 0x10,&local_20);
  if (*DAT_01a1f100 == local_10) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

