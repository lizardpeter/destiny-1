
void FUN_00799a50(long param_1)

{
  if (*(int *)(param_1 + 0x30) != 0x15) {
    FUN_00799a70();
    return;
  }
  if (*(int *)(param_1 + 0x34) == 3) {
    FUN_00783ed0(0x14);
    return;
  }
  FUN_00799fa0();
  return;
}

