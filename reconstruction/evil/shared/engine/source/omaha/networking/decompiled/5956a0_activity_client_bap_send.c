
undefined8
FUN_005956a0(long param_1,undefined8 param_2,int param_3,undefined8 param_4,int param_5,
            undefined4 param_6)

{
  undefined4 uVar1;
  undefined8 *puVar2;
  undefined8 uVar3;
  undefined1 local_d8 [8];
  undefined8 *local_d0;
  undefined8 local_c8;
  ulong local_c0 [12];
  long local_60;
  
  local_60 = *DAT_01a1f100;
  if (param_3 == 8) {
    FUN_00595800(param_1,param_4);
  }
  else {
    FUN_000b54b0(local_d8,0x1df0d,0x19,s_send_message_via_bap_0163eb88);
    local_c0[4] = 0;
    local_c0[5] = 0;
    local_c0[6] = 0;
    local_c0[7] = 0;
    local_c0[0] = 0;
    local_c0[1] = 0;
    local_c0[2] = 0;
    local_c0[3] = 0;
    local_c0[9] = 0;
    local_c0[8] = 0;
    FUN_001271d0(local_c0 + 3);
    puVar2 = local_d0;
    local_c0[0] = local_c0[0] | 4;
    *(undefined1 *)(local_d0 + 1) = 0;
    *local_d0 = 0;
    *(undefined1 *)local_d0 = 1;
    *(undefined4 *)((long)local_d0 + 9) = 0;
    *(int *)((long)local_d0 + 1) = param_3;
    local_c0[3] = param_2;
    thunk_FUN_012aa7c6((long)local_d0 + 0xd,param_4,(long)param_5);
    *(int *)((long)puVar2 + 5) = param_5;
    *(undefined4 *)((long)local_d0 + 9) = param_6;
    uVar1 = *(undefined4 *)(param_1 + 0x7c);
    FUN_00072050(&local_c8,0xffffffff);
    FUN_0055aa80(uVar1,0x11,local_c0,local_d0,param_5 + 0xd,local_c8);
    FUN_000b54e0(local_d8);
  }
  if (*DAT_01a1f100 == local_60) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

