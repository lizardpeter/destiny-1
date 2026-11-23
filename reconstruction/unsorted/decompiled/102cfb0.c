
void FUN_0102cfb0(undefined8 param_1,undefined8 param_2,undefined8 param_3,undefined8 param_4)

{
  long *plVar1;
  ulong uVar2;
  undefined8 local_48;
  undefined8 uStack_40;
  uint local_30 [2];
  long local_28;
  
  plVar1 = DAT_01a1f100;
  local_28 = *DAT_01a1f100;
  local_30[0] = 0;
  local_48 = 0;
  uStack_40 = 0;
  FUN_0102cc90(local_30);
  FUN_000730b0(param_4,&local_48,0x80);
  if ((local_30[0] == 0xffffffff) || ((int)local_48 == -1)) {
    local_30[0] = 0xffffffff;
  }
  else {
    uVar2 = (ulong)((local_30[0] & 0x1fff) * DAT_02689800);
    FUN_0030d690((DAT_026897f8 + uVar2) -
                 ((long)DAT_02689818 & *(ulong *)(DAT_026897f8 + 8 + uVar2)),&local_48,param_1);
  }
  if (*plVar1 == local_28) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

