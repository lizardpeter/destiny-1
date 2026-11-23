
void FUN_00576070(undefined8 param_1,long *param_2)

{
  long *plVar1;
  undefined4 uVar2;
  undefined8 uVar3;
  long *plVar4;
  long lVar5;
  undefined1 local_39;
  long local_38;
  
  plVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  uVar3 = FUN_0056b260();
  plVar4 = (long *)(**(code **)(*param_2 + 0x18))(param_2);
  if (*plVar4 != 0) {
    uVar2 = FUN_01009850(uVar3);
    lVar5 = FUN_0056dc00(uVar3,3,uVar2,plVar4);
    if (lVar5 != 0) {
      uVar3 = FUN_0056b260();
      plVar4 = (long *)(**(code **)(*param_2 + 0x18))(param_2);
      lVar5 = 0;
      if (*plVar4 != 0) {
        uVar2 = FUN_01009850(uVar3);
        lVar5 = FUN_0056dc00(uVar3,3,uVar2,plVar4);
      }
      (**(code **)(*param_2 + 0x40))(param_2);
      FUN_00556c70(3,lVar5 + 0x68,param_2,&local_39);
    }
  }
  if (*plVar1 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

