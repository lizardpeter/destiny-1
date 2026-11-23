
void FUN_004ed070(long param_1)

{
  if (*(int *)(param_1 + 0x2f0) != -1) {
    FUN_0063fbe0();
    *(undefined4 *)(param_1 + 0x2f0) = 0xffffffff;
  }
  if (*(int *)(param_1 + 0x2f4) != -1) {
    FUN_0063fbe0();
    *(undefined4 *)(param_1 + 0x2f4) = 0xffffffff;
  }
  if (*(int *)(param_1 + 0x2f8) != -1) {
    FUN_0063fc40();
    *(undefined4 *)(param_1 + 0x2f8) = 0xffffffff;
  }
  if (*(int *)(param_1 + 0x2fc) != -1) {
    FUN_0063fc10();
    *(undefined4 *)(param_1 + 0x2fc) = 0xffffffff;
  }
  if (*(int *)(param_1 + 0x300) != -1) {
    FUN_0063fc70();
    *(undefined4 *)(param_1 + 0x300) = 0xffffffff;
  }
  if (*(int *)(param_1 + 0x304) != -1) {
    FUN_0063fca0();
    *(undefined4 *)(param_1 + 0x304) = 0xffffffff;
  }
  FUN_00641990(param_1);
  FUN_00641990(param_1 + 0x128);
  FUN_00643fa0(param_1 + 0x250);
  FUN_00642900(param_1 + 700);
  FUN_00272610(param_1 + 0x2e8);
  FUN_00272610(param_1 + 0x2ec);
  *(undefined8 *)(param_1 + 0x300) = 0xffffffffffffffff;
  *(undefined8 *)(param_1 + 0x2f8) = 0xffffffffffffffff;
  *(undefined8 *)(param_1 + 0x2f0) = 0xffffffffffffffff;
  *(undefined1 *)(param_1 + 0x308) = 0;
  return;
}

