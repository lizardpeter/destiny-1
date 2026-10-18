
void FUN_0056d110(long param_1,undefined8 *param_2)

{
  int iVar1;
  undefined8 uVar2;
  long lVar3;
  long *plVar4;
  undefined8 local_7620;
  long local_7618;
  undefined4 local_7610;
  long local_7608;
  undefined4 local_7600;
  undefined1 local_75f8 [30160];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  uVar2 = FUN_00021860(&DAT_026bc270);
  local_7620 = *param_2;
  local_7610 = *(undefined4 *)(param_1 + 0x4ffc4);
  local_7600 = *(undefined4 *)(param_1 + 0x4ffcc);
  local_7608 = (long)*(int *)(param_1 + 0x4ffc8);
  if ((ulong)*(uint *)(param_1 + 0x4ffc0) == 0xffffffff) {
    local_7618 = 0;
  }
  else {
    local_7618 = param_1 + 0x40a0 + (ulong)*(uint *)(param_1 + 0x4ffc0);
  }
  lVar3 = FUN_0056cb20(param_1,5,&local_7620);
  if (lVar3 == 0) {
    FUN_00575990(uVar2,2);
  }
  else {
    if (*(char *)(lVar3 + 0x28) == '\x02') {
      *(undefined1 *)(lVar3 + 0x28) = 3;
    }
    local_7610 = *(undefined4 *)(param_1 + 0x4ffc4);
    local_7600 = *(undefined4 *)(param_1 + 0x4ffcc);
    local_7608 = (long)*(int *)(param_1 + 0x4ffc8);
    if ((ulong)*(uint *)(param_1 + 0x4ffc0) == 0xffffffff) {
      local_7618 = 0;
    }
    else {
      local_7618 = param_1 + 0x40a0 + (ulong)*(uint *)(param_1 + 0x4ffc0);
    }
    plVar4 = (long *)FUN_0056cc40(param_1,&local_7618,lVar3 + 0x16,&local_7620,5,5);
    lVar3 = local_7608;
    if (plVar4 == (long *)0x0) {
      FUN_00575990(uVar2,4);
    }
    else {
      thunk_FUN_012aa7c6(local_75f8,plVar4,local_7608);
      if (*plVar4 == 0) {
        FUN_0056f9c0(plVar4);
      }
      else {
        iVar1 = thunk_FUN_012aa826(local_75f8,plVar4,lVar3);
        if (iVar1 != 0) {
          FUN_0056f9c0(local_75f8,plVar4);
        }
      }
      thunk_FUN_012aa7c6(plVar4,param_2,lVar3);
    }
  }
  if (*DAT_01a1f100 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

