
void FUN_00574dc0(undefined1 *param_1,undefined1 *param_2)

{
  long lVar1;
  
  *param_1 = *param_2;
  *(undefined2 *)(param_1 + 2) = *(undefined2 *)(param_2 + 2);
  param_1[4] = param_2[4];
  lVar1 = 0;
  *(undefined2 *)(param_1 + 6) = *(undefined2 *)(param_2 + 6);
  *(undefined4 *)(param_1 + 8) = *(undefined4 *)(param_2 + 8);
  do {
    *(undefined2 *)(param_1 + lVar1 * 4 + 0xc) = *(undefined2 *)(param_2 + lVar1 * 4 + 0xc);
    *(undefined2 *)(param_1 + lVar1 * 4 + 0xe) = *(undefined2 *)(param_2 + lVar1 * 4 + 0xe);
    lVar1 = lVar1 + 1;
  } while (lVar1 != 0x20);
  return;
}

