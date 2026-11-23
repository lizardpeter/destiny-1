
undefined8 FUN_00bc3590(undefined8 param_1,long param_2,byte *param_3,undefined8 param_4)

{
  uint uVar1;
  uint7 uVar3;
  undefined8 uVar2;
  byte *pbVar4;
  uint uVar5;
  undefined **local_38;
  undefined8 uStack_30;
  undefined8 local_28;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  uStack_30 = 0;
  local_38 = &PTR_FUN_01943f30;
  local_28 = 0xffffffff;
  FUN_006eca80(&local_38,param_4,*(undefined4 *)(param_2 + 8));
  uVar5 = (*(int *)(param_3 + 8) << 0x12) >> 0x12;
  uVar1 = uVar5 & 0xfffffffe;
  uVar3 = (uint7)(uint3)(uVar1 >> 8);
  if (uVar1 == 0xfffffffe) {
    uVar2 = CONCAT71(uVar3,1);
    if (((*(int *)(param_3 + 8) << 4) >> 0x12) + 0x1f >> 5 < 1) goto LAB_00bc3640;
    pbVar4 = *(byte **)param_3;
  }
  else {
    uVar2 = CONCAT71(uVar3,1);
    pbVar4 = param_3;
    if (uVar5 != 0) goto LAB_00bc3640;
  }
  uVar2 = CONCAT71(uVar3,1);
  if ((*pbVar4 & 1) != 0) {
    uVar2 = FUN_002c8290(*(undefined4 *)PTR_DAT_0191a858,param_3,0,*(undefined8 *)(param_2 + 0x38),
                         &local_38);
  }
LAB_00bc3640:
  if (*DAT_01a1f100 != local_20) {
    uVar2 = thunk_FUN_012aa7f6();
    return uVar2;
  }
  return uVar2;
}

