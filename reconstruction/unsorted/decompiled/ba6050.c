
void FUN_00ba6050(undefined8 *param_1,undefined8 param_2)

{
  undefined8 *puVar1;
  
  puVar1 = (undefined8 *)FUN_00068570();
  *param_1 = param_2;
  param_1[1] = 0xffffffffffffffff;
  *(undefined4 *)((long)param_1 + 0x12dc) = 0;
  *(undefined4 *)(param_1 + 0x25d) = 0xffffffff;
  thunk_FUN_012aa986((long)param_1 + 0x12ec,0,0xa1);
  FUN_00ba8980(param_1 + 2);
  thunk_FUN_012aa986(param_1 + 0x247,0,0xa4);
  *(undefined4 *)(param_1 + 0x25d) = 0;
  *(undefined4 *)((long)param_1 + 0x12dc) = 1;
  *(undefined8 *)((long)param_1 + 0x12ec) = *puVar1;
  *(undefined1 *)((long)param_1 + 0x138c) = 1;
  FUN_00bb6850(*param_1,puVar1);
  FUN_000f8520(*param_1,0);
  return;
}

