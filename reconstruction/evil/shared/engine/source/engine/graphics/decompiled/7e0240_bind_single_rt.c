
void FUN_007e0240(long param_1,undefined8 param_2)

{
  undefined8 uVar1;
  long *plVar2;
  undefined4 uVar3;
  undefined4 uVar4;
  undefined4 local_40 [2];
  undefined4 local_38 [2];
  long local_30;
  
  plVar2 = DAT_01a1f100;
  local_30 = *DAT_01a1f100;
  uVar1 = *(undefined8 *)(param_1 + 0x50);
  FUN_00f8f0e0(uVar1,0,param_2);
  FUN_00f8f0e0(uVar1,1,0);
  FUN_00f8f0e0(uVar1,2,0);
  FUN_00f8f0e0(uVar1,3,0);
  FUN_00f7eec0(uVar1,0);
  FUN_00992780(local_38);
  FUN_00f81d60(local_38,0,7);
  FUN_00f81ec0(local_38,7);
  FUN_00f81b40(local_38,0);
  FUN_00f81b30(local_38,0);
  FUN_00f7e950(uVar1,local_38[0]);
  FUN_00992780(local_40);
  FUN_00f819f0(local_40,0);
  FUN_00f7e7c0(uVar1,0,local_40[0]);
  FUN_00f7e7c0(uVar1,1,local_40[0]);
  FUN_00f7e7c0(uVar1,2,local_40[0]);
  FUN_00f7e7c0(uVar1,3,local_40[0]);
  FUN_00f7e740(uVar1,0xf);
  uVar3 = FUN_00263ef0(param_2);
  uVar4 = FUN_00f82690(param_2);
  FUN_00f8f4b0(DAT_0165fe9c,DAT_0165fe9c,uVar1,0,0,uVar3,uVar4);
  if (*plVar2 == local_30) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

