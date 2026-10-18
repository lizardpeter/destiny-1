
void FUN_007dea90(long *param_1,long param_2)

{
  int *piVar1;
  int iVar2;
  uint uVar3;
  int iVar4;
  
  *(undefined1 *)(*param_1 + 0x2d8) = DAT_018dcc30;
  FUN_0006ac60(param_2);
  piVar1 = (int *)(param_2 + 0x18);
  do {
    iVar2 = *piVar1;
    LOCK();
    iVar4 = *piVar1;
    if (iVar2 == iVar4) {
      *piVar1 = 0;
      iVar4 = iVar2;
    }
    UNLOCK();
  } while (iVar2 != iVar4);
  *(undefined4 *)(param_2 + 0x1c) = 0;
  *(undefined4 *)(param_2 + 0x24) = 0;
  *(undefined1 *)(param_2 + 0x28) = 0;
  *(undefined4 *)(param_2 + 0x730) = 0;
  *(undefined4 *)(param_2 + 0x830) = 0;
  *(undefined4 *)(param_2 + 0x930) = 0;
  thunk_FUN_012aa986(param_2 + 0x30,0,0x604);
  *(int *)(*param_1 + 0x2d0) = *(int *)(*param_1 + 0x2d0) + 1;
  uVar3 = *(uint *)(*param_1 + 0x2c8);
  *(long *)(*param_1 + 200 + ((ulong)uVar3 & 0x3f) * 8) = param_2;
  *(int *)(*param_1 + 0xc0) = *(int *)(*param_1 + 0xc0) + 1;
  *(uint *)(param_2 + 0x930) = uVar3 & 0x3f;
  *(int *)(*param_1 + 0x2c8) = *(int *)(*param_1 + 0x2c8) + 1;
  *(uint *)(*param_1 + 0xb4) = *(uint *)(*param_1 + 0xb4) ^ 1;
  FUN_007ef890(&DAT_026e4840,param_2 + 0x1c);
  return;
}

