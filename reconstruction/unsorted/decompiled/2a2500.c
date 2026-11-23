
void FUN_002a2500(long param_1,undefined8 param_2)

{
  undefined8 *puVar1;
  long lVar2;
  
  FUN_002a2620();
  FUN_002a0800(param_1 + 0x68);
  *(undefined1 *)(param_1 + 100) = 0;
  *(undefined8 *)(param_1 + 8) = param_2;
  *(undefined4 *)(param_1 + 0x3c) = 0;
  *(undefined4 *)(param_1 + 0x40) = 0;
  *(undefined4 *)(param_1 + 0x44) = 0;
  *(undefined8 *)(param_1 + 0x48) = 0xffffffffffffffff;
  *(undefined4 *)(param_1 + 0x50) = 0xffffffff;
  *(undefined1 *)(param_1 + 0x10) = 0;
  *(undefined1 *)(param_1 + 0x14) = 0;
  *(undefined4 *)(param_1 + 0x18) = 0;
  *(undefined1 *)(param_1 + 0x50a8) = 0;
  thunk_FUN_012aa986(param_1 + 0x50b0,0,0x6b0);
  lVar2 = 0;
  do {
    puVar1 = (undefined8 *)(param_1 + 0x5118 + lVar2);
    puVar1[2] = 0;
    puVar1[1] = 0;
    *puVar1 = 0;
    *(undefined8 *)(param_1 + 0x5118 + lVar2) = 0xffffffff811c9dc5;
    puVar1 = (undefined8 *)(param_1 + 0x5120 + lVar2);
    puVar1[1] = 0;
    *puVar1 = 0;
    lVar2 = lVar2 + 0x18;
  } while ((int)lVar2 != 0x4b0);
  *(undefined4 *)(param_1 + 0x55c8) = 0x811c9dc5;
  *(undefined1 *)(param_1 + 0x55cc) = 0;
  FUN_01018280(param_1 + 0x56a4);
  *(undefined4 *)(param_1 + 0x5730) = 0xffffffff;
  FUN_000a0760(param_1 + 0x5760);
  *(undefined1 *)(param_1 + 0x5764) = 0;
  *(undefined1 *)(param_1 + 5) = 1;
  return;
}

