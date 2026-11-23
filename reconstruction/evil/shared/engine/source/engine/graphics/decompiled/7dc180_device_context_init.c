
void FUN_007dc180(undefined8 *param_1)

{
  int *piVar1;
  int *piVar2;
  int iVar3;
  int iVar4;
  long lVar5;
  
  *param_1 = 0;
  *(undefined4 *)(param_1 + 2) = 0;
  *(undefined4 *)((long)param_1 + 0x14) = 0;
  FUN_00f8eb70(param_1 + 0xc);
  FUN_00f8eb70(param_1 + 0x1d8);
  piVar1 = (int *)(param_1 + 2);
  thunk_FUN_012aa986(piVar1,0,0x2830);
  FUN_007dc270(param_1);
  piVar2 = (int *)((long)param_1 + 0x14);
  *(undefined1 *)((long)param_1 + 0x26) = 1;
  param_1[3] = DAT_015b6068;
  do {
    iVar3 = *piVar1;
    LOCK();
    iVar4 = *piVar1;
    if (iVar3 == iVar4) {
      *piVar1 = 0;
      iVar4 = iVar3;
    }
    UNLOCK();
  } while (iVar3 != iVar4);
  do {
    iVar3 = *piVar2;
    LOCK();
    iVar4 = *piVar2;
    if (iVar3 == iVar4) {
      *piVar2 = 0;
      iVar4 = iVar3;
    }
    UNLOCK();
  } while (iVar3 != iVar4);
  *(undefined1 *)((long)param_1 + 0x25ec) = 0xff;
  lVar5 = 8;
  do {
    *(undefined4 *)(&DAT_026df3a8 + lVar5) = 1;
    *(undefined8 *)((long)&DAT_026df3b0 + lVar5) = 0;
    lVar5 = lVar5 + 0x10;
  } while ((int)lVar5 != 0x3838);
  return;
}

