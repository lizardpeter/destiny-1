
long FUN_007dcce0(long *param_1)

{
  long lVar1;
  int *piVar2;
  uint uVar3;
  int iVar4;
  long lVar5;
  int iVar6;
  ulong uVar7;
  long lVar8;
  long lVar9;
  
  uVar3 = *(uint *)(*param_1 + 0x2dc);
  *(uint *)(*param_1 + 0x2dc) = uVar3 + 1;
  lVar9 = (ulong)uVar3 * 0x938;
  lVar5 = *param_1;
  lVar1 = lVar5 + 0x2e0 + lVar9;
  FUN_0006ac60(lVar1);
  piVar2 = (int *)(lVar5 + 0x2f8 + lVar9);
  do {
    iVar4 = *piVar2;
    LOCK();
    iVar6 = *piVar2;
    if (iVar4 == iVar6) {
      *piVar2 = 0;
      iVar6 = iVar4;
    }
    UNLOCK();
  } while (iVar4 != iVar6);
  *(undefined4 *)(lVar5 + 0x2fc + lVar9) = 0;
  *(undefined4 *)(lVar5 + 0x304 + lVar9) = 0;
  *(undefined1 *)(lVar5 + 0x308 + lVar9) = 0;
  *(undefined4 *)(lVar5 + 0xa10 + lVar9) = 0;
  *(undefined4 *)(lVar5 + 0xb10 + lVar9) = 0;
  *(undefined4 *)(lVar5 + 0xc10 + lVar9) = 0;
  thunk_FUN_012aa986(lVar5 + 0x310 + lVar9,0,0x604);
  FUN_007ef890(&DAT_026e4840,lVar5 + 0x2fc + lVar9);
  param_1[0xb] = lVar1;
  FUN_007dc270(param_1,0);
  uVar7 = (ulong)*(uint *)(*param_1 + 0xb4);
  lVar8 = uVar7 * 0xe60;
  param_1[10] = (long)(param_1 + uVar7 * 0x1cc + 0xc);
  *(undefined1 *)((long)param_1 + lVar8 + 0x22b) = 0xff;
  *(undefined2 *)((long)param_1 + lVar8 + 0x229) = 0xffff;
  *(undefined4 *)((long)param_1 + lVar8 + 0x225) = 0xffffffff;
  *(undefined1 *)((long)param_1 + lVar8 + 0x152) = 0xff;
  *(undefined2 *)(param_1 + uVar7 * 0x1cc + 0x2a) = 0xffff;
  param_1[uVar7 * 0x1cc + 0x29] = -1;
  param_1[uVar7 * 0x1cc + 0x28] = -1;
  param_1[uVar7 * 0x1cc + 0x27] = -1;
  param_1[uVar7 * 0x1cc + 0x26] = -1;
  thunk_FUN_012aa986((long)param_1 + lVar8 + 0x15a,0xff,0xc4);
  *(undefined4 *)(lVar5 + 0x300 + lVar9) = *(undefined4 *)(*param_1 + 0xb4);
  FUN_007ef9c0(&DAT_026e4840,param_1 + 10);
  return lVar1;
}

