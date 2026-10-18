
void FUN_002bcb90(long param_1,undefined8 param_2,char param_3,int param_4)

{
  undefined8 uVar1;
  undefined1 local_128 [256];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  FUN_010156f0(local_128,s___s_sessions__s_fields__default_01625f4c,&DAT_015badb0,param_2);
  if (param_3 != '\0') {
    FUN_00065140(local_128,s__members_01625b2f,0x100);
  }
  if (param_4 != 0) {
    uVar1 = FUN_002c05d0(param_4);
    FUN_01009470(local_128,s__npLanguage__s_01625b38,uVar1);
  }
  FUN_002c18e0(param_1 + 8,1,0,local_128);
  if (*DAT_01a1f100 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

