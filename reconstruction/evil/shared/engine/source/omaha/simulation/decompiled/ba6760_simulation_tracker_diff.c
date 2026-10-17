
void FUN_00ba6760(undefined8 *param_1,undefined8 param_2,undefined4 param_3,undefined8 param_4)

{
  int iVar1;
  int iVar2;
  long lVar3;
  
  iVar1 = FUN_00bb58c0(*param_1);
  if (iVar1 != -1) {
    lVar3 = FUN_00bb54d0(*param_1,iVar1);
    if (lVar3 != 0) {
      lVar3 = FUN_0075f130(*(undefined8 *)(lVar3 + 0x10));
      FUN_00b9b720(param_1 + 2);
      if (((lVar3 != 0) && (*(uint *)(lVar3 + 0x8c48) < 0xb)) &&
         ((0x3f0U >> (*(uint *)(lVar3 + 0x8c48) & 0x1f) & 1) != 0)) {
        iVar1 = *(int *)((long)param_1 + 0xc);
        iVar2 = FUN_00b74390(lVar3);
        if (iVar1 != iVar2) {
          FUN_00ba6830(param_1,param_2,param_3,param_4);
          return;
        }
      }
      return;
    }
  }
  FUN_00b9b720(param_1 + 2);
  return;
}

