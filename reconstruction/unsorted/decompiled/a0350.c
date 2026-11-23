
void FUN_000a0350(undefined8 param_1,long *param_2,int *param_3,uint param_4,undefined4 param_5)

{
  uint uVar1;
  long *plVar2;
  undefined8 local_180;
  undefined8 uStack_178;
  long *plStack_170;
  ulong uStack_168;
  undefined8 local_160;
  undefined8 local_158;
  long local_138 [32];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  local_180 = 0;
  uStack_178 = 0;
  local_158 = 0;
  local_160 = 0;
  if (0 < (int)param_4) {
    plVar2 = local_138 + 1;
    uVar1 = param_4;
    do {
      *plVar2 = (long)*param_3;
      plVar2[-1] = *param_2;
      plVar2 = plVar2 + 2;
      param_2 = param_2 + 1;
      param_3 = param_3 + 1;
      uVar1 = uVar1 - 1;
    } while (uVar1 != 0);
  }
  plStack_170 = local_138;
  uStack_168 = (ulong)param_4;
  thunk_FUN_012aafe6(param_1,&local_180,param_5);
  if (*DAT_01a1f100 == local_38) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

