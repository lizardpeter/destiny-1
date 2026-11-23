
ulong FUN_007d3cb0(int param_1,ulong param_2,undefined8 param_3,undefined4 param_4,
                  undefined8 param_5,undefined1 param_6,short param_7,short param_8,ulong param_9)

{
  long lVar1;
  char cVar2;
  uint uVar3;
  long lVar4;
  ulong uVar5;
  long lVar6;
  uint local_78;
  long local_70;
  undefined4 local_64;
  undefined4 local_60 [2];
  undefined1 local_58 [32];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_78 = 0xffffffff;
  if (((param_7 != 0) && (param_8 != 0)) && ((param_2 & 8) != 0)) {
    local_60[0] = FUN_007e3c40(param_4);
    cVar2 = FUN_00f7dab0(local_60);
    if (cVar2 != '\0') {
      FUN_00f859b0(&local_64,(param_1 == 1) * '\x03' + '\a',local_60[0],1);
      if (param_1 == 1) {
        local_64 = 8;
      }
      if (param_9 == 0) {
        local_70 = 0;
        uVar5 = FUN_00f83530(local_58,param_7,param_8,1,param_6,local_60[0],local_64,0,0);
        uVar3 = FUN_000cdf40(1,(int)(uVar5 >> 0x20) + (int)uVar5,&local_70,0,1,1);
        param_9 = -(uVar5 >> 0x20) & ((uVar5 >> 0x20) - 1) + local_70;
      }
      else {
        uVar3 = FUN_000cdf40(1,0,0,0,1,1);
      }
      if (uVar3 != 0xffffffff) {
        lVar4 = (ulong)(((uint)((int)uVar3 >> 0xd) >> 0x12 | 0x3ff) & (int)uVar3 >> 0xd) * 0x40;
        lVar6 = *DAT_01a238a0;
        lVar1 = *(long *)(lVar6 + 0x10 + lVar4);
        uVar5 = (ulong)((uVar3 & 0x1fff) * *(int *)(lVar6 + 0x30 + lVar4));
        lVar6 = (lVar1 + uVar5) -
                ((long)*(int *)(lVar6 + 0x34 + lVar4) & *(ulong *)(lVar1 + 8 + uVar5));
        FUN_00f83530(lVar6,param_7,param_8,1,param_6,local_60[0],local_64,0,0);
        FUN_00f841b0(lVar6,param_9 >> 8 & 0xffffffff);
        FUN_000ce4b0(uVar3);
        local_78 = uVar3;
      }
    }
  }
  if (*DAT_01a1f100 == local_38) {
    return (ulong)local_78;
  }
  uVar5 = thunk_FUN_012aa7f6();
  return uVar5;
}

