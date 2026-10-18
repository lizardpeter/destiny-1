
void FUN_007e15d0(long param_1,ulong param_2,undefined8 param_3,int param_4,undefined4 param_5)

{
  int iVar1;
  long lVar2;
  long lVar3;
  
  if (*(char *)(param_1 + 0x26) != '\0') {
    FUN_00f7f1e0(*(undefined8 *)(param_1 + 0x50),
                 *(undefined4 *)(&DAT_015d13c0 + (param_2 & 0xffffffff) * 4));
    lVar3 = *(long *)(*(long *)(param_1 + 0x1d70) + 0x30);
    iVar1 = *(int *)(*(long *)(param_1 + 0x1d70) + 0x38);
    FUN_00f7f840(*(undefined8 *)(param_1 + 0x50),param_5);
    lVar3 = (ulong)(uint)((iVar1 * 2 + 2) * param_4) + lVar3;
    FUN_00f7f7e0(*(undefined8 *)(param_1 + 0x50),lVar3);
    lVar2 = *(long *)(param_1 + 0x50);
    FUN_00f8df60(lVar2 + 0xc0,lVar2,lVar2 + 0x80);
    FUN_00f7f320(lVar2,param_5,lVar3);
    FUN_00f8e880(lVar2 + 0xc0,lVar2,lVar2 + 0x80);
    return;
  }
  return;
}

