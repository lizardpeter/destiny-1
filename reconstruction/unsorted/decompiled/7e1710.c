
void FUN_007e1710(long param_1,uint param_2,undefined4 param_3,undefined8 param_4,undefined4 param_5
                 )

{
  long lVar1;
  
  if (*(char *)(param_1 + 0x26) != '\0') {
    FUN_00f7f890(*(undefined8 *)(param_1 + 0x50),param_5);
    FUN_00f7f1e0(*(undefined8 *)(param_1 + 0x50),*(undefined4 *)(&DAT_015d13c0 + (ulong)param_2 * 4)
                );
    lVar1 = *(long *)(param_1 + 0x50);
    FUN_00f8df60(lVar1 + 0xc0,lVar1,lVar1 + 0x80);
    FUN_00f7f260(lVar1,param_3);
    FUN_00f8e880(lVar1 + 0xc0,lVar1,lVar1 + 0x80);
    FUN_00f7f890(*(undefined8 *)(param_1 + 0x50),1);
    return;
  }
  return;
}

