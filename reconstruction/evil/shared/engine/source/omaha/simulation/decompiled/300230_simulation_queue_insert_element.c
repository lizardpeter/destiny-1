
undefined8 FUN_00300230(int param_1,undefined4 param_2,undefined8 param_3)

{
  long lVar1;
  long *plVar2;
  char cVar3;
  undefined8 uVar4;
  int iVar5;
  undefined1 uStack_10119;
  long lStack_10118;
  undefined1 auStack_10110 [20];
  undefined4 uStack_100fc;
  int iStack_100f0;
  int iStack_100e0;
  undefined1 auStack_10038 [65544];
  
  lVar1 = *DAT_01a1f100;
  cVar3 = FUN_00240e60();
  uStack_10119 = 0;
  if (cVar3 == '\0') {
    uStack_100fc = 1;
    FUN_00072240(auStack_10110,auStack_10038,0x10000);
    FUN_000723b0(auStack_10110,1);
    cVar3 = FUN_002c9a80(param_2,param_3,auStack_10110,0);
    FUN_00072560(auStack_10110,0);
    if (cVar3 != '\0') {
      cVar3 = FUN_00072210(auStack_10110);
      if (cVar3 == '\0') {
        iVar5 = (int)(((uint)(iStack_100f0 + 7 + iStack_100e0 >> 0x1f) >> 0x1d) + 7 +
                     iStack_100f0 + iStack_100e0) >> 3;
        lStack_10118 = 0;
        plVar2 = *(long **)(DAT_02689508 + (long)param_1 * 8);
        if (plVar2 != (long *)0x0) {
          cVar3 = (**(code **)(*plVar2 + 8))();
          if (cVar3 != '\0') {
            iVar5 = FUN_002c8e10(param_2);
            iVar5 = (int)(iVar5 + 7 + ((uint)(iVar5 + 7 >> 0x1f) >> 0x1d)) >> 3;
          }
        }
        FUN_00300b00(param_1,iVar5,&lStack_10118);
        if (lStack_10118 != 0) {
          thunk_FUN_012aa7c6(*(undefined8 *)(lStack_10118 + 8),auStack_10038,
                             (long)((int)(((uint)(iStack_100f0 + 7 + iStack_100e0 >> 0x1f) >> 0x1d)
                                          + 7 + iStack_100f0 + iStack_100e0) >> 3));
          FUN_00300b90(lStack_10118);
          uStack_10119 = 1;
        }
      }
    }
  }
  if (*DAT_01a1f100 == lVar1) {
    return CONCAT71((int7)((ulong)*DAT_01a1f100 >> 8),uStack_10119);
  }
  uVar4 = thunk_FUN_012aa7f6();
  return uVar4;
}

