
void FUN_00ba6470(undefined8 *param_1)

{
  undefined8 *puVar1;
  long *plVar2;
  undefined4 local_30 [2];
  long local_28;
  
  plVar2 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  local_30[0] = 0;
  puVar1 = param_1 + 2;
  FUN_00ba8980(puVar1);
  FUN_00ba89d0(puVar1);
  FUN_00b9b720(puVar1);
  FUN_00913a60(local_30,(long)param_1 + 0x123c);
  *(undefined4 *)(param_1 + 0x247) = local_30[0];
  *(undefined4 *)((long)param_1 + 0xc) = 0xffffffff;
  FUN_00bb6ae0(*param_1);
  if (*plVar2 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

