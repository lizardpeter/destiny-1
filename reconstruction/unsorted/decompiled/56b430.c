
void FUN_0056b430(undefined8 *param_1)

{
  long *plVar1;
  undefined4 local_2c;
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  FUN_0056b5f0();
  param_1[0xb] = 0;
  param_1[10] = 0;
  param_1[9] = 0;
  param_1[8] = 0;
  param_1[7] = 0;
  param_1[6] = 0;
  param_1[5] = 0;
  param_1[4] = 0;
  param_1[3] = 0;
  param_1[2] = 0;
  param_1[1] = 0;
  *param_1 = 0;
  *(undefined2 *)param_1 = 1;
  *(undefined2 *)((long)param_1 + 2) = 1;
  *(undefined2 *)((long)param_1 + 0xc) = 1;
  *(undefined2 *)((long)param_1 + 0xe) = 1;
  *(undefined2 *)((long)param_1 + 0x12) = 0x14;
  *(undefined2 *)(param_1 + 3) = 1;
  *(undefined2 *)((long)param_1 + 0x1a) = 1;
  *(undefined2 *)((long)param_1 + 0x24) = 1;
  *(undefined2 *)((long)param_1 + 0x26) = 10;
  *(undefined2 *)(param_1 + 6) = 1;
  *(undefined2 *)((long)param_1 + 0x32) = 1;
  *(undefined2 *)((long)param_1 + 0x36) = 0x29a;
  *(undefined2 *)((long)param_1 + 0x34) = 1;
  *(undefined2 *)(param_1 + 7) = 1;
  *(undefined2 *)((long)param_1 + 0x46) = 1;
  *(undefined2 *)(param_1 + 9) = 1;
  *(undefined2 *)((long)param_1 + 0x4a) = 1;
  *(undefined4 *)((long)param_1 + 0x54) = 0x10001;
  local_2c = 0;
  FUN_0056d2f0(param_1,0,0x14,&local_2c);
  FUN_0056d2f0(param_1,1,1,&local_2c);
  FUN_0056d2f0(param_1,2,0xe7,&local_2c);
  FUN_0056d2f0(param_1,3,1,&local_2c);
  FUN_0056d2f0(param_1,4,1,&local_2c);
  FUN_0056d2f0(param_1,5,1,&local_2c);
  FUN_0056d2f0(param_1,6,1,&local_2c);
  FUN_0056d2f0(param_1,7,1,&local_2c);
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

