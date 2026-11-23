
bool FUN_0055f820(undefined8 param_1,undefined8 param_2,char *param_3,char *param_4,
                 undefined8 param_5,int *param_6)

{
  undefined4 uVar1;
  char cVar2;
  
  *param_4 = *param_3;
  cVar2 = *param_3;
  if (cVar2 == '\x01') {
    *(undefined8 *)(param_4 + 1) = *(undefined8 *)(param_3 + 1);
    FUN_002a3620(param_4 + 1);
    uVar1 = swap_bytes(*(undefined4 *)(param_3 + 9));
    *(undefined4 *)(param_4 + 9) = uVar1;
    uVar1 = swap_bytes(*(undefined4 *)(param_3 + 0xd));
    *(undefined4 *)(param_4 + 0xd) = uVar1;
    thunk_FUN_012aa7c6(param_4 + 0x11,param_3 + 0x11,(long)*(int *)(param_3 + 0xd));
    *param_6 = *(int *)(param_3 + 0xd) + 0x11;
  }
  return cVar2 == '\x01';
}

