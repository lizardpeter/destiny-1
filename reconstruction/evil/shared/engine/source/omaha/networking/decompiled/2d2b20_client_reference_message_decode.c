
undefined8
FUN_002d2b20(undefined8 param_1,undefined8 param_2,undefined8 param_3,undefined4 *param_4,
            int *param_5)

{
  char cVar1;
  undefined4 uVar2;
  undefined8 uVar3;
  undefined1 local_110 [20];
  undefined4 local_fc;
  undefined1 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_fc = 1;
  FUN_00072240(local_110,param_1,0x1df00);
  local_40 = 0;
  FUN_00072400(local_110);
  cVar1 = FUN_002c9a90(*(undefined4 *)PTR_DAT_0191a0c0,local_110,param_2,param_2,1);
  if (cVar1 != '\0') {
    cVar1 = FUN_002c9a90(*(undefined4 *)PTR_DAT_01996050,local_110,param_5,param_5,1);
    if ((cVar1 != '\0') && (*param_5 != -1)) {
      cVar1 = FUN_002c9a90(*param_5,local_110,param_3,param_3,1);
      FUN_00072650(local_110);
      uVar3 = 0;
      if (cVar1 != '\0') {
        uVar2 = FUN_001d4990(*param_5);
        *param_4 = uVar2;
        uVar3 = 1;
      }
      goto LAB_002d2be1;
    }
  }
  FUN_00072650(local_110);
  uVar3 = 0;
LAB_002d2be1:
  if (*DAT_01a1f100 == local_38) {
    return uVar3;
  }
  uVar3 = thunk_FUN_012aa7f6();
  return uVar3;
}

