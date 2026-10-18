
undefined8
FUN_0081a480(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4,
            undefined8 param_5,ulong param_6,ushort param_7)

{
  undefined8 uVar1;
  undefined4 local_40;
  undefined4 local_3c;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (param_3 < 2) {
    FUN_00f859b0(&local_3c,2,param_4,1);
    if ((param_7 >> 2 & 1) != 0) {
      local_3c = 8;
    }
    uVar1 = FUN_00f83530(param_5,param_1,param_2,1,1,param_4,local_3c,0,0);
  }
  else {
    FUN_00f859b0(&local_40,0xb,param_4,1);
    if ((param_7 >> 2 & 1) != 0) {
      local_40 = 8;
    }
    uVar1 = FUN_00f83ab0(param_5,param_1,param_2,param_3,1,param_4,local_40);
  }
  FUN_00f841b0(param_5,param_6 >> 8 & 0xffffffff);
  if (*DAT_01a1f100 != local_38) {
    uVar1 = thunk_FUN_012aa7f6();
    return uVar1;
  }
  return uVar1;
}

