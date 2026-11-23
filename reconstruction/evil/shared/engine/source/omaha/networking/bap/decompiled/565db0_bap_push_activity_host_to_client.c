
undefined8
FUN_00565db0(undefined8 param_1,undefined8 param_2,undefined2 *param_3,undefined8 param_4,
            undefined8 param_5)

{
  undefined4 uVar1;
  int iVar2;
  long *plVar3;
  undefined8 uVar4;
  undefined8 local_88;
  undefined8 local_80;
  undefined8 uStack_78;
  undefined8 uStack_70;
  undefined8 uStack_68;
  undefined8 local_60;
  undefined8 uStack_58;
  undefined8 uStack_50;
  undefined8 uStack_48;
  undefined8 local_40;
  undefined8 local_38;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  local_60 = 0;
  uStack_58 = 0;
  uStack_50 = 0;
  uStack_48 = 0;
  local_80 = 0;
  uStack_78 = 0;
  uStack_70 = 0;
  uStack_68 = 0;
  local_38 = 0;
  local_40 = 0;
  FUN_001271d0(&uStack_68);
  plVar3 = (long *)FUN_0055af60(*param_3);
  uVar1 = (**(code **)(*plVar3 + 8))(plVar3);
  plVar3 = (long *)FUN_0055d370(uVar1);
  uVar1 = (**(code **)(*plVar3 + 0x28))(plVar3,param_3);
  iVar2 = FUN_00559c30(uVar1);
  if (iVar2 == 3) {
    FUN_00072050(&local_88,0xffffffff);
    FUN_0055aa80(uVar1,9,&local_80,param_5,0x1df11,local_88);
  }
  if (*DAT_01a1f100 == local_28) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),1);
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

