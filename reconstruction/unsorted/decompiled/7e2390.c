
void FUN_007e2390(long param_1,uint param_2)

{
  undefined1 *puVar1;
  long lVar2;
  
  if (param_2 != 0) {
    puVar1 = &DAT_026f248c + (ulong)param_2 * 0xe0;
    lVar2 = (ulong)param_2 * 0xe0 + 0x26f2438;
    if (*(uint *)(param_1 + 0x27d8) == param_2) {
      FUN_007e2000(param_1,lVar2,0);
      *(undefined4 *)(param_1 + 0x27d8) = 0;
      *puVar1 = 0;
    }
    if (*(uint *)(param_1 + 0x27dc) == param_2) {
      FUN_007e2000(param_1,lVar2,1);
      *(undefined4 *)(param_1 + 0x27dc) = 0;
      *puVar1 = 0;
    }
    if (*(uint *)(param_1 + 0x27e0) == param_2) {
      FUN_007e2000(param_1,lVar2,2);
      *(undefined4 *)(param_1 + 0x27e0) = 0;
      *puVar1 = 0;
    }
    if (*(uint *)(param_1 + 0x27e4) == param_2) {
      FUN_007e2000(param_1,lVar2,3);
      *(undefined4 *)(param_1 + 0x27e4) = 0;
      *puVar1 = 0;
    }
  }
  return;
}

