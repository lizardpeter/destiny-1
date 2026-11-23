
void FUN_002b4600(long param_1,undefined8 *param_2,long param_3)

{
  long lVar1;
  undefined1 local_c0 [64];
  undefined1 local_80 [48];
  undefined1 local_50 [24];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  FUN_002447a0(param_2,local_80);
  FUN_002b8460(local_80,local_50);
  *(undefined8 *)(param_1 + 0x1c0) = *param_2;
  FUN_002b8260(param_1 + 0x1c8);
  FUN_002e93e0();
  lVar1 = param_1 + 0x250;
  *(undefined4 *)(param_1 + 0x248) = 1;
  FUN_00065030(lVar1,param_3,0x2d);
  if ((*(byte *)(param_3 + 0x70) & 1) == 0) {
    FUN_002bc910(param_1 + 0x90,local_50);
    FUN_002bcb90(param_1 + 0x90,lVar1,1,0);
  }
  else {
    local_c0[0] = 0;
    FUN_00065030(local_c0,param_3 + 0x30,0x3c);
    FUN_002ba060(param_1 + 0x128,local_50);
    FUN_002ba1a0(param_1 + 0x128,local_50,local_c0,0,0);
  }
  FUN_002bca10(param_1,local_50,param_1 + 0x1f8,0x4e);
  FUN_002bd1a0(param_1,lVar1);
  *(undefined2 *)(param_1 + 0x27d) = 0;
  *(undefined1 *)(param_1 + 0x27f) = 1;
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

