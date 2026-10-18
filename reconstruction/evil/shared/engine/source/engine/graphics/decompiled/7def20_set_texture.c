
void FUN_007def20(long param_1,undefined4 param_2,ulong param_3,undefined *param_4)

{
  char cVar1;
  
  param_3 = param_3 & 0xffffffff;
  switch(param_2) {
  case 1:
    if (param_4 == (undefined *)0x0) {
      param_4 = PTR_DAT_01a1f4b8;
    }
    if (param_4 != *(undefined **)(&DAT_00001ef8 + param_3 * 8 + param_1)) {
      cVar1 = FUN_00f84710(param_4);
      if (cVar1 == '\0') {
        param_4 = PTR_DAT_01a1f4b8;
      }
      FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,1,param_3,1,param_4);
      *(undefined **)(&DAT_00001ef8 + param_3 * 8 + param_1) = param_4;
    }
    break;
  case 2:
    if (param_4 == (undefined *)0x0) {
      param_4 = PTR_DAT_01a1f4b8;
    }
    if (param_4 != *(undefined **)((long)&PTR_DAT_00001f78 + param_3 * 8 + param_1)) {
      cVar1 = FUN_00f84710(param_4);
      if (cVar1 == '\0') {
        param_4 = PTR_DAT_01a1f4b8;
      }
      FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,2,param_3,1,param_4);
      *(undefined **)((long)&PTR_DAT_00001f78 + param_3 * 8 + param_1) = param_4;
    }
    break;
  case 3:
    if (param_4 == (undefined *)0x0) {
      param_4 = PTR_DAT_01a1f4b8;
    }
    if (param_4 != *(undefined **)(param_1 + 0x1ff8 + param_3 * 8)) {
      cVar1 = FUN_00f84710(param_4);
      if (cVar1 == '\0') {
        param_4 = PTR_DAT_01a1f4b8;
      }
      FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,3,param_3,1,param_4);
      *(undefined **)(param_1 + 0x1ff8 + param_3 * 8) = param_4;
    }
    break;
  case 4:
    if (param_4 == (undefined *)0x0) {
      param_4 = PTR_DAT_01a1f4b8;
    }
    if (param_4 != *(undefined **)(param_1 + 0x20f8 + param_3 * 8)) {
      cVar1 = FUN_00f84710(param_4);
      if (cVar1 == '\0') {
        param_4 = PTR_DAT_01a1f4b8;
      }
      FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,5,param_3,1,param_4);
      *(undefined **)(param_1 + 0x20f8 + param_3 * 8) = param_4;
    }
    break;
  case 5:
    if (param_4 == (undefined *)0x0) {
      param_4 = PTR_DAT_01a1f4b8;
    }
    if (param_4 != *(undefined **)(&DAT_00001e78 + param_3 * 8 + param_1)) {
      cVar1 = FUN_00f84710(param_4);
      if (cVar1 == '\0') {
        param_4 = PTR_DAT_01a1f4b8;
      }
      FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,0,param_3,1,param_4);
      *(undefined **)(&DAT_00001e78 + param_3 * 8 + param_1) = param_4;
    }
    break;
  case 6:
    if (param_4 == (undefined *)0x0) {
      param_4 = PTR_DAT_01a1f4b8;
    }
    if (param_4 != *(undefined **)(param_1 + 0x2178 + param_3 * 8)) {
      cVar1 = FUN_00f84710(param_4);
      if (cVar1 == '\0') {
        param_4 = PTR_DAT_01a1f4b8;
      }
      FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,6,param_3,1,param_4);
      *(undefined **)(param_1 + 0x2178 + param_3 * 8) = param_4;
    }
    break;
  case 7:
    if (param_4 == (undefined *)0x0) {
      param_4 = PTR_DAT_01a1f4b8;
    }
    if (param_4 != *(undefined **)(param_1 + 0x2078 + param_3 * 8)) {
      cVar1 = FUN_00f84710(param_4);
      if (cVar1 == '\0') {
        param_4 = PTR_DAT_01a1f4b8;
      }
      FUN_00f8afd0(*(long *)(param_1 + 0x50) + 0xc0,4,param_3,1,param_4);
      *(undefined **)(param_1 + 0x2078 + param_3 * 8) = param_4;
    }
  }
  return;
}

