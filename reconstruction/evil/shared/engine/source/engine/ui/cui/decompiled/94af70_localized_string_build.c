
undefined8 FUN_0094af70(undefined8 param_1,long *param_2)

{
  long lVar1;
  long lVar2;
  long lVar3;
  char cVar4;
  long lVar5;
  undefined8 uVar6;
  int *piVar7;
  int local_258 [2];
  undefined4 local_250 [2];
  undefined8 local_248;
  undefined4 local_240 [2];
  undefined8 auStack_238 [63];
  long local_40;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  lVar5 = 0;
  if (*param_2 != 0) {
    lVar5 = *param_2 + (long)param_2;
  }
  local_40 = 0;
  if ((ulong)*(uint *)(param_2 + 1) != 0) {
    piVar7 = (int *)(lVar5 + 0x10);
    lVar5 = (ulong)*(uint *)(param_2 + 1) << 5;
    do {
      if (((*(byte *)((long)piVar7 + 0xb) & 3) == 2) && (*piVar7 != -0x7ee3623b)) {
        local_250[0] = 0x811c9dc5;
        local_248 = 0;
        local_258[0] = -0x7ee3623b;
        if ((*(byte *)((long)piVar7 + 0xb) & 3) == 2) {
          local_258[0] = *piVar7;
        }
        cVar4 = FUN_0094b0f0(local_258,local_250);
        lVar3 = local_40;
        if (cVar4 != '\0') {
          lVar1 = local_40 + 1;
          lVar2 = local_40 * 4;
          local_40 = lVar1;
          if (local_240 + lVar2 != (undefined4 *)0x0) {
            local_240[lVar2] = local_250[0];
            auStack_238[lVar3 * 2] = local_248;
          }
        }
      }
      piVar7 = piVar7 + 8;
      lVar5 = lVar5 + -0x20;
    } while (lVar5 != 0);
  }
  FUN_008da890(param_1,param_2,local_240,local_40);
  if (*DAT_01a1f100 != local_38) {
    uVar6 = thunk_FUN_012aa7f6();
    return uVar6;
  }
  return param_1;
}

