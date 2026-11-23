
ulong FUN_00819f80(undefined4 param_1,undefined4 param_2,undefined8 param_3,undefined8 param_4,
                  ulong param_5)

{
  undefined4 uVar1;
  ulong uVar2;
  ulong uVar3;
  ulong uVar4;
  ulong local_58;
  uint local_50;
  uint local_4c;
  undefined4 local_44;
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_40[0] = (undefined4)param_3;
  FUN_00f859b0(&local_44,4,param_3,1);
  local_50 = 0;
  local_4c = 0;
  local_58 = 0;
  uVar1 = FUN_00f7d750(local_40);
  uVar2 = FUN_00f7dba0(param_4,param_1,param_2,1,uVar1,1,local_44,0,&local_50,&local_58);
  FUN_00f7e410(param_4,1);
  uVar3 = (ulong)local_4c;
  FUN_000b8510(param_4,param_5 >> 8 & 0xffffffff);
  FUN_000bd400(param_4,param_5 >> 8 & 0xffffffff);
  uVar4 = -uVar3 & (uVar3 - 1) + (uVar2 & 0xffffffff) + param_5;
  uVar3 = uVar4 >> 8;
  FUN_001e8120(param_4,uVar3 & 0xffffffff);
  FUN_0005b0d0(param_4,uVar3 & 0xffffffff);
  uVar3 = -(local_58 >> 0x20) & ((local_58 >> 0x20) - 1) + local_50 + uVar4;
  FUN_00f7e570(param_4,uVar3 >> 8);
  if (*DAT_01a1f100 == local_38) {
    return (ulong)(uint)(((int)local_58 - (int)param_5) + (int)uVar3) | uVar2 & 0xffffffff00000000;
  }
  uVar2 = thunk_FUN_012aa7f6();
  return uVar2;
}

