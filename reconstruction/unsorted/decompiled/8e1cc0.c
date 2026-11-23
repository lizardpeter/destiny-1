
void FUN_008e1cc0(undefined8 *param_1,undefined4 param_2,undefined4 param_3)

{
  long *plVar1;
  int iVar2;
  undefined4 uVar3;
  undefined8 *puVar4;
  undefined8 uVar5;
  undefined8 local_30;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  FUN_008e3de0();
  *param_1 = &PTR_FUN_01949fb0;
  *(undefined4 *)(param_1 + 0x6c) = 0;
  FUN_008e5430(0,param_1,2);
  puVar4 = (undefined8 *)FUN_001c0900(param_1);
  iVar2 = (**(code **)*puVar4)(puVar4);
  if (iVar2 == 2) {
    *(undefined1 *)((long)param_1 + 0x364) = 1;
    uVar5 = FUN_001c0900(param_1);
    FUN_008e9bc0(uVar5,0);
  }
  else {
    *(undefined1 *)((long)param_1 + 0x364) = 0;
  }
  uVar3 = FUN_009236d0(param_2);
  uVar3 = FUN_006ed8f0(uVar3);
  FUN_00072050(&local_30,uVar3);
  plVar1 = DAT_01a1f100;
  param_1[0x6b] = local_30;
  *(undefined1 *)((long)param_1 + 0x365) = 1;
  *(undefined4 *)(param_1 + 0x6d) = param_3;
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

