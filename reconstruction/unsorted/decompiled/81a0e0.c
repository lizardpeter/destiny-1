
ulong FUN_0081a0e0(undefined4 param_1,undefined4 param_2,uint param_3,undefined4 param_4,
                  undefined8 param_5,ulong param_6,ushort param_7)

{
  ulong uVar1;
  ulong uVar2;
  undefined4 uVar3;
  ulong *puVar4;
  undefined4 local_48;
  undefined4 local_44;
  ulong local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_40 = 0;
  if (param_3 < 2) {
    FUN_00f859b0(&local_44,2,param_4,1);
    if ((param_7 >> 2 & 1) != 0) {
      local_44 = 8;
    }
    puVar4 = (ulong *)0x0;
    if ((param_7 & 0x4000) != 0) {
      puVar4 = &local_40;
    }
    param_3 = 1;
    uVar3 = local_44;
  }
  else {
    FUN_00f859b0(&local_48,0xb,param_4,1);
    if ((param_7 >> 2 & 1) != 0) {
      local_48 = 8;
    }
    puVar4 = (ulong *)0x0;
    uVar3 = local_48;
  }
  uVar1 = FUN_00f81f80(param_5,param_1,param_2,param_3,param_4,uVar3,0,0,puVar4,0);
  FUN_00c2e290(param_5,param_6 >> 8);
  uVar2 = uVar1;
  if ((int)local_40 != 0) {
    uVar2 = -(local_40 >> 0x20) & ((local_40 >> 0x20) - 1) + (uVar1 & 0xffffffff) + param_6;
    FUN_00f82aa0(param_5,uVar2 >> 8);
    FUN_00f82620(param_5,1);
    uVar2 = (local_40 & 0xffffffff) + (uVar2 - param_6);
  }
  if (*DAT_01a1f100 != local_38) {
    uVar2 = thunk_FUN_012aa7f6();
    return uVar2;
  }
  return uVar2 & 0xffffffff | uVar1 & 0xffffffff00000000;
}

