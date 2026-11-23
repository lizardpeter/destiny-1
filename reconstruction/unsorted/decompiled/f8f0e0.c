
void FUN_00f8f0e0(undefined8 param_1,undefined4 param_2,undefined8 *param_3)

{
  char cVar1;
  int iVar2;
  undefined4 uVar3;
  undefined8 *puVar4;
  undefined8 local_58;
  undefined8 local_50;
  undefined8 local_48;
  undefined8 local_40;
  undefined8 local_38;
  undefined4 local_30;
  long local_28;
  
  local_28 = *DAT_01a1f100;
  if (param_3 == (undefined8 *)0x0) {
    puVar4 = (undefined8 *)0x0;
  }
  else {
    local_38 = param_3[4];
    local_30 = *(undefined4 *)(param_3 + 5);
    local_40 = param_3[3];
    local_48 = param_3[2];
    local_58 = *param_3;
    local_50 = param_3[1];
    cVar1 = FUN_00f82b60(&local_58);
    if (cVar1 == '\0') {
      cVar1 = FUN_00f82b70(&local_58);
      if (cVar1 != '\0') {
        iVar2 = FUN_000732a0(&local_58);
        if (iVar2 == 0) {
          iVar2 = FUN_002836d0(&local_58);
          if (iVar2 != 0) {
            FUN_00f82640(&local_58,0);
            uVar3 = FUN_00f826a0(&local_58);
            FUN_00f825e0(&local_58,uVar3);
            uVar3 = FUN_00f82ae0(&local_58);
            FUN_00f82660(&local_58,uVar3);
            uVar3 = FUN_002836d0(&local_58);
            FUN_00417af0(&local_58,uVar3);
          }
        }
      }
    }
    puVar4 = &local_58;
  }
  FUN_00f7edb0(param_1,param_2,puVar4);
  if (*DAT_01a1f100 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

