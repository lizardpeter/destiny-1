
void FUN_008e6470(undefined8 *param_1)

{
  long *plVar1;
  long *plVar2;
  undefined8 local_38;
  undefined4 local_30;
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  FUN_008e3de0();
  *param_1 = &PTR_FUN_0194a390;
  FUN_008e5430(0,param_1,2);
  plVar2 = (long *)FUN_001c0900(param_1);
  local_30 = *(undefined4 *)(DAT_01905108 + 1);
  local_38 = *DAT_01905108;
  FUN_00923790();
  (**(code **)(*plVar2 + 0x48))(plVar2,&local_38);
  FUN_008e9ba0(plVar2,1);
  FUN_008e9bc0(plVar2,0);
  *(undefined4 *)(param_1 + 0x6b) = 0xffffffff;
  *(undefined4 *)((long)param_1 + 0x35c) = 0xffffffff;
  *(undefined2 *)(param_1 + 0x6c) = 0;
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

