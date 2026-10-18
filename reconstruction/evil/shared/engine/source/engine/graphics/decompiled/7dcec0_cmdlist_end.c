
void FUN_007dcec0(long *param_1,undefined8 param_2,int param_3)

{
  int iVar1;
  int iVar2;
  int *piVar3;
  long lVar4;
  uint uVar5;
  
  uVar5 = 0x18;
  if (param_3 == 1) {
    uVar5 = 0x118;
  }
  lVar4 = param_1[10];
  if ((ulong)(*(long *)(lVar4 + 8) - *(long *)(lVar4 + 0x10)) < (ulong)uVar5) {
    FUN_00f7feb0(lVar4,uVar5,2);
    lVar4 = param_1[10];
  }
  FUN_007ef3a0(&DAT_026e4840,DAT_026df291 == '\0' || param_3 == 1,
               *(undefined4 *)(param_1[0xb] + 0x1c),param_1[0xb],lVar4);
  if (param_3 == 1) {
    *(undefined4 *)(*param_1 + 0xbc) = *(undefined4 *)(*param_1 + 0xb8);
    *(undefined4 *)(*param_1 + 0xb8) =
         *(undefined4 *)(DAT_026e4840 + (ulong)*(uint *)(param_1[0xb] + 0x1c) * 8);
    FUN_00f81220(param_1[10]);
  }
  FUN_007db810(param_1[0xb],param_1[10],2,uVar5,1);
  *(undefined8 *)param_1[10] = ((undefined8 *)param_1[10])[2];
  *(undefined8 *)(param_1[10] + 0x80) = *(undefined8 *)(param_1[10] + 0x90);
  *(bool *)(param_1[0xb] + 0x28) = param_3 != 0;
  piVar3 = (int *)(param_1[0xb] + 0x18);
  do {
    iVar1 = *piVar3;
    LOCK();
    iVar2 = *piVar3;
    if (iVar1 == iVar2) {
      *piVar3 = 1;
      iVar2 = iVar1;
    }
    UNLOCK();
  } while (iVar1 != iVar2);
  lVar4 = param_1[0xb];
  if ((*(int *)(lVar4 + 0x430) != 0) || (*(int *)(lVar4 + 0x530) != 0)) {
    *(int *)(*param_1 + 0x2d0) = *(int *)(*param_1 + 0x2d0) + 1;
    uVar5 = *(uint *)(*param_1 + 0x2c8);
    *(long *)(*param_1 + 200 + ((ulong)uVar5 & 0x3f) * 8) = lVar4;
    *(int *)(*param_1 + 0xc0) = *(int *)(*param_1 + 0xc0) + 1;
    *(uint *)(lVar4 + 0x930) = uVar5 & 0x3f;
    *(int *)(*param_1 + 0x2c8) = *(int *)(*param_1 + 0x2c8) + 1;
    *(uint *)(*param_1 + 0xb4) = *(uint *)(*param_1 + 0xb4) ^ 1;
  }
  param_1[0xb] = 0;
  param_1[10] = 0;
  return;
}

