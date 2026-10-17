
void FUN_001e39c0(undefined4 *param_1,int param_2)

{
  int iVar1;
  undefined1 local_50 [40];
  long local_28;
  
  local_28 = *DAT_01a1f100;
  param_1[1] = param_2;
  param_1[3] = 0;
  *(undefined1 *)(param_1 + 4) = 0;
  iVar1 = FUN_000b9710(param_2,local_50);
  if (iVar1 != -1) {
    do {
      FUN_000b8000(iVar1,-(param_2 - 2U < 3) & 2U | 1);
      iVar1 = FUN_000b9880(local_50);
    } while (iVar1 != -1);
  }
  switch(param_1[1]) {
  case 0:
    iVar1 = FUN_002b0460();
    break;
  case 1:
    iVar1 = FUN_002b0540();
    break;
  case 2:
    iVar1 = FUN_002b0600();
    break;
  case 3:
    iVar1 = FUN_002b0770();
    break;
  case 4:
    param_1[2] = 0xffffffff;
  default:
    goto switchD_001e3a4e_default;
  }
  param_1[2] = iVar1 + -1;
switchD_001e3a4e_default:
  *param_1 = 1;
  if (*DAT_01a1f100 != local_28) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

