
void FUN_005568c0(undefined4 param_1,long param_2,long *param_3,long param_4,long param_5,
                 undefined1 *param_6)

{
  uint *puVar1;
  short sVar2;
  bool bVar3;
  int iVar4;
  undefined8 uVar5;
  long *plVar6;
  long lVar7;
  byte bVar8;
  bool bVar9;
  char local_39;
  long local_38;
  
  local_38 = *DAT_01a1f100;
  uVar5 = FUN_005494c0();
  iVar4 = FUN_0054d110(uVar5,param_1);
  bVar9 = true;
  bVar8 = (byte)param_1;
  if (iVar4 != -1) {
    lVar7 = (long)((int)(short)param_1 >> 5);
    if ((*(uint *)(param_5 + lVar7 * 4) >> (bVar8 & 0x1f) & 1) == 0) {
      (**(code **)(*param_3 + 0x38))(param_3,iVar4);
      uVar5 = FUN_00346d20();
      iVar4 = FUN_00349c10(uVar5,iVar4);
      puVar1 = (uint *)(param_5 + lVar7 * 4);
      *puVar1 = *puVar1 | 1 << (bVar8 & 0x1f);
      bVar9 = iVar4 == 2;
    }
  }
  plVar6 = (long *)FUN_0025cbd0();
  iVar4 = (**(code **)(*plVar6 + 0x558))(plVar6,param_1);
  if (iVar4 != -1) {
    lVar7 = (long)((int)(short)param_1 >> 5);
    if ((*(uint *)(param_4 + lVar7 * 4) >> (bVar8 & 0x1f) & 1) == 0) {
      (**(code **)(*param_3 + 0x38))(param_3,iVar4);
      uVar5 = FUN_00346d20();
      iVar4 = FUN_00349c10(uVar5,iVar4);
      puVar1 = (uint *)(param_4 + lVar7 * 4);
      *puVar1 = *puVar1 | 1 << (bVar8 & 0x1f);
      if (iVar4 != 2) {
        bVar9 = false;
      }
    }
  }
  if (param_2 != 0) {
    lVar7 = 0;
    do {
      sVar2 = *(short *)(param_2 + 0x26 + lVar7 * 2);
      bVar3 = bVar9;
      if (sVar2 != -1) {
        local_39 = '\0';
        FUN_005568c0(sVar2,0,param_3,param_4,param_5,&local_39);
        bVar3 = false;
        if (local_39 != '\0') {
          bVar3 = bVar9;
        }
      }
      bVar9 = bVar3;
      lVar7 = lVar7 + 1;
    } while ((char)lVar7 != '\b');
  }
  *param_6 = bVar9;
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

