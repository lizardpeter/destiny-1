
void FUN_000ad5a0(undefined4 param_1,undefined4 param_2,undefined4 param_3,undefined4 param_4,
                 int param_5)

{
  int iVar1;
  long lVar2;
  
  iVar1 = DAT_01ad4840;
  lVar2 = (long)param_5 * 0x10;
  *(undefined4 *)(&DAT_01ad40d0 + lVar2 + 800 + (long)DAT_01ad4840 * 0x3b0) = param_1;
  *(undefined4 *)(&DAT_01ad40d0 + lVar2 + 0x324 + (long)iVar1 * 0x3b0) = param_2;
  *(undefined4 *)(&DAT_01ad40d0 + lVar2 + 0x328 + (long)iVar1 * 0x3b0) = param_3;
  *(undefined4 *)(&DAT_01ad40d0 + lVar2 + 0x32c + (long)iVar1 * 0x3b0) = param_4;
  return;
}

