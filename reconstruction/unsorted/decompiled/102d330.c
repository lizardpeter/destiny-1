
void FUN_0102d330(undefined8 param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  long *plVar1;
  undefined4 uVar2;
  undefined8 uVar3;
  undefined8 uVar4;
  char local_48 [8];
  char local_40 [8];
  long local_38;
  
  plVar1 = DAT_01a1f100;
  local_38 = *DAT_01a1f100;
  local_40[0] = '\0';
  local_48[0] = '\0';
  FUN_002c9a90(*(undefined4 *)PTR_DAT_01974c00,param_4,local_40,local_40,1);
  FUN_002c9a90(*(undefined4 *)PTR_DAT_01974be0,param_4,local_48,local_48,1);
  FUN_001c0950(param_1,(int)local_40[0],(int)local_48[0]);
  uVar2 = FUN_001c0630(param_1);
  uVar3 = FUN_001c0900(param_1);
  uVar4 = FUN_001c0900(param_1);
  FUN_002c9a90(uVar2,param_4,uVar3,uVar4,1);
  uVar2 = FUN_001c0740(param_1);
  uVar3 = FUN_001c0910(param_1);
  uVar4 = FUN_001c0910(param_1);
  FUN_002c9a90(uVar2,param_4,uVar3,uVar4,1);
  if (*plVar1 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

