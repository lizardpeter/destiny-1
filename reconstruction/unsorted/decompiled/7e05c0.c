
void FUN_007e05c0(long *param_1,undefined8 param_2,undefined4 param_3,undefined4 param_4,int param_5
                 ,int param_6,undefined8 param_7,undefined4 param_8,undefined4 param_9)

{
  undefined4 *puVar1;
  long lVar2;
  undefined1 local_88 [32];
  undefined1 local_68 [32];
  undefined1 local_48 [16];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar2 = param_1[10];
  puVar1 = (undefined4 *)FUN_00f7feb0(lVar2,0x18,4);
  *puVar1 = param_8;
  puVar1[1] = param_9;
  puVar1[2] = param_3;
  puVar1[3] = param_4;
  puVar1[4] = param_5;
  puVar1[5] = param_6;
  FUN_00f7d180(local_48,puVar1,0x18);
  FUN_00f7d010(local_48,0x10);
  lVar2 = lVar2 + 0xc0;
  FUN_00f8b500(lVar2,0,0,1,local_48);
  FUN_00f83e80(local_68,param_2,0);
  FUN_00f839a0(local_68,0x10);
  FUN_00f83e80(local_88,param_7,0);
  FUN_00f839a0(local_88,0x6d);
  FUN_00f8afd0(lVar2,0,0,1,local_68);
  FUN_00f8b1f0(lVar2,0,0,1,local_88);
  FUN_007e0780(param_1,*(undefined8 *)(*param_1 + 0x68),
               (int)(param_5 + 7 + ((uint)(param_5 + 7 >> 0x1f) >> 0x1d)) >> 3,
               (int)(param_6 + 7 + ((uint)(param_6 + 7 >> 0x1f) >> 0x1d)) >> 3,1,1);
  FUN_00f8afd0(lVar2,0,0,1,0);
  FUN_00f8b1f0(lVar2,0,0,1,0);
  FUN_00f8b500(lVar2,0,0,1,0);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

