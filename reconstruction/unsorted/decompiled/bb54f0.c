
void FUN_00bb54f0(long param_1,undefined8 param_2,long param_3,undefined8 param_4,undefined8 param_5
                 ,undefined8 param_6,undefined8 param_7)

{
  char cVar1;
  undefined4 uVar2;
  undefined8 uVar3;
  long lVar4;
  int iVar5;
  undefined8 local_48;
  undefined8 local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  if (*(int *)(param_1 + 8) != 1) {
    param_1 = param_1 + -0x57e0;
    iVar5 = -1;
    local_40 = param_2;
    do {
      iVar5 = iVar5 + 1;
      if (2 < iVar5) {
        lVar4 = FUN_00ba0990(param_2);
        if (lVar4 != 0) {
          FUN_0029bf30(lVar4,(int)*(char *)(param_3 + 0x604),param_3 + 4);
        }
        goto LAB_00bb55c3;
      }
      local_48 = *(undefined8 *)(param_1 + 0x18278);
      param_1 = param_1 + 0x18258;
      cVar1 = FUN_000685a0(&local_48,&local_40);
    } while (cVar1 == '\0');
    uVar3 = FUN_00ba2b80(param_1);
    FUN_00b518a0(uVar3,param_3,param_4,param_5,param_6,param_7);
  }
LAB_00bb55c3:
  FUN_00ba0c30(param_4,0);
  FUN_00ba0f10(param_5);
  cVar1 = FUN_00906f70();
  if (cVar1 != '\0') {
    FUN_00ba0f60(param_6);
  }
  uVar2 = FUN_00011e50();
  FUN_00ba0c30(param_7,uVar2);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

