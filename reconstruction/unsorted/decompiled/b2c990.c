
void FUN_00b2c990(long *param_1)

{
  long lVar1;
  int iVar2;
  long lVar3;
  undefined8 uVar4;
  int iVar5;
  int local_e0;
  int local_dc;
  long local_a0;
  long local_98;
  long local_20;
  
  local_20 = *DAT_01a1f100;
  if ((int)param_1[4] != 0) {
    lVar1 = *param_1;
    lVar3 = DAT_026553b0;
    if (DAT_026553a8 == '\0') {
      lVar3 = FUN_000694d0();
    }
    if ((long)*(int *)((long)param_1 + 0x14) <= lVar3 - lVar1) {
      iVar2 = (int)param_1[4];
      if (iVar2 == 0) {
        uVar4 = 0;
      }
      else {
        local_a0 = (long)param_1 + (long)*(int *)((long)param_1 + 0x1c) + 0x24;
        iVar5 = (int)param_1[3] - *(int *)((long)param_1 + 0x1c);
        uVar4 = 1;
        local_e0 = iVar2;
        if (iVar5 < iVar2) {
          local_98 = (long)param_1 + 0x24;
          local_dc = iVar2 - iVar5;
          uVar4 = 2;
          local_e0 = iVar5;
        }
      }
      iVar2 = thunk_FUN_002e7600(param_1[1],&local_a0,&local_e0,uVar4);
      if (iVar2 < 1) {
        if (iVar2 != -2) {
          *(int *)(param_1 + 2) = iVar2;
        }
      }
      else if ((int)param_1[4] < iVar2) {
        *(undefined8 *)((long)param_1 + 0x1c) = 0;
      }
      else {
        *(int *)((long)param_1 + 0x1c) = (*(int *)((long)param_1 + 0x1c) + iVar2) % (int)param_1[3];
        *(int *)(param_1 + 4) = (int)param_1[4] - iVar2;
      }
    }
  }
  if (*DAT_01a1f100 == local_20) {
    return;
  }
  thunk_FUN_012aa7f6();
  return;
}

