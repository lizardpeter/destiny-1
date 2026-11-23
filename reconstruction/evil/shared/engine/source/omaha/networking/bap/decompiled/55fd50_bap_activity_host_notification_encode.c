
undefined8
FUN_0055fd50(undefined8 param_1,undefined8 param_2,char *param_3,char *param_4,undefined8 param_5,
            int *param_6)

{
  undefined4 uVar1;
  int iVar2;
  
  *param_4 = *param_3;
  if (*param_3 == '\x02') {
    uVar1 = swap_bytes(*(undefined4 *)(param_3 + 1));
    *(undefined4 *)(param_4 + 1) = uVar1;
    uVar1 = swap_bytes(*(undefined4 *)(param_3 + 5));
    *(undefined4 *)(param_4 + 5) = uVar1;
    thunk_FUN_012aa7c6(param_4 + 9,param_3 + 9,(long)*(int *)(param_3 + 5));
    iVar2 = *(int *)(param_3 + 5) + 9;
  }
  else {
    if (*param_3 != '\x01') {
      return 0;
    }
    uVar1 = swap_bytes(*(undefined4 *)(param_3 + 1));
    *(undefined4 *)(param_4 + 1) = uVar1;
    uVar1 = swap_bytes(*(undefined4 *)(param_3 + 5));
    *(undefined4 *)(param_4 + 5) = uVar1;
    uVar1 = swap_bytes(*(undefined4 *)(param_3 + 9));
    *(undefined4 *)(param_4 + 9) = uVar1;
    thunk_FUN_012aa7c6(param_4 + 0xd,param_3 + 0xd,(long)*(int *)(param_3 + 5));
    iVar2 = *(int *)(param_3 + 5) + 0xd;
  }
  *param_6 = iVar2;
  return 1;
}

