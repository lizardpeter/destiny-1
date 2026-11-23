
void FUN_002b47a0(char *param_1,undefined8 param_2,undefined8 param_3,long param_4,
                 undefined8 param_5)

{
  long *plVar1;
  undefined4 uVar2;
  undefined1 local_3b0 [520];
  undefined1 local_1a8 [48];
  undefined1 local_178 [24];
  undefined1 *local_160;
  undefined1 *puStack_158;
  undefined8 uStack_150;
  undefined1 *puStack_148;
  undefined8 local_140;
  undefined8 uStack_138;
  undefined8 uStack_130;
  undefined8 uStack_128;
  undefined8 local_120;
  undefined8 uStack_118;
  undefined8 uStack_110;
  undefined8 uStack_108;
  undefined8 local_100;
  long lStack_f8;
  undefined8 uStack_f0;
  undefined4 uStack_e8;
  undefined4 uStack_e4;
  undefined8 local_e0;
  undefined1 **ppuStack_d8;
  undefined8 uStack_d0;
  undefined8 uStack_c8;
  undefined8 local_c0;
  undefined8 uStack_b8;
  undefined8 uStack_b0;
  undefined8 uStack_a8;
  undefined8 local_a0;
  undefined8 local_98;
  undefined1 local_90 [48];
  long local_60;
  
  local_60 = *DAT_01a1f100;
  if (*param_1 != '\0') {
    thunk_FUN_012ab7d6();
    *param_1 = '\0';
  }
  FUN_002b8460(param_3,local_178);
  FUN_00066250(param_5,local_3b0,0x200,0);
  local_90[0] = 0;
  FUN_002e9a70(param_4 + 0x3c,local_90,0x2d);
  FUN_00065030(local_1a8,local_90,0x2e);
  uStack_138 = 0;
  uStack_130 = 0;
  uStack_128 = 0;
  uStack_150 = 1;
  local_140 = 1;
  local_c0 = 0;
  uStack_b8 = 0;
  uStack_b0 = 0;
  uStack_a8 = 0;
  local_e0 = 0;
  ppuStack_d8 = (undefined1 **)0x0;
  uStack_d0 = 0;
  uStack_c8 = 0;
  local_98 = 0;
  local_a0 = 0;
  uStack_118 = 0;
  uStack_110 = 0;
  uStack_108 = 0;
  local_100 = 0;
  local_120 = 0x30;
  lStack_f8 = (ulong)((int)&local_120 + 0xc0d1a109) << 0x20;
  uStack_e8 = 0xffffffff;
  uStack_e4 = 0;
  uStack_f0 = 0x90;
  local_160 = local_3b0;
  puStack_158 = local_1a8;
  puStack_148 = local_178;
  uVar2 = FUN_00245ef0(param_2);
  ppuStack_d8 = &local_160;
  _uStack_e8 = CONCAT44(uStack_e4,uVar2);
  uStack_f0 = CONCAT44(1,(undefined4)uStack_f0);
  thunk_FUN_012ab7e6();
  thunk_FUN_012ab7f6(&local_120);
  plVar1 = DAT_01a1f100;
  param_1[0] = '\x01';
  param_1[1] = '\0';
  if (*plVar1 == local_60) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

