
void FUN_0028d5e0(undefined8 param_1,undefined8 param_2,long param_3)

{
  long lVar1;
  undefined4 uVar2;
  long *plVar3;
  int *piVar4;
  short sVar5;
  int iVar6;
  undefined8 uVar7;
  long lVar8;
  undefined4 local_40 [2];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  plVar3 = (long *)FUN_0025a550();
  piVar4 = (int *)(**(code **)(*plVar3 + 0x2a8))(plVar3);
  if ((piVar4 != (int *)0x0) && (0 < *piVar4)) {
    if (param_3 == 0) {
      uVar7 = CONCAT62((int6)((ulong)param_1 >> 0x10),1);
      do {
        FUN_0028a7f0(param_1,(int)uVar7 + -1,param_2,0);
        sVar5 = (short)uVar7;
        uVar7 = CONCAT62((int6)((ulong)uVar7 >> 0x10),sVar5 + 1);
      } while ((int)sVar5 < *piVar4);
    }
    else {
      plVar3 = (long *)(piVar4 + 2);
      iVar6 = 0;
      do {
        lVar1 = *plVar3;
        FUN_0028a7f0(param_1,iVar6,param_2,param_3);
        sVar5 = (short)iVar6;
        lVar8 = (long)*(short *)((long)plVar3 + (long)sVar5 * 0x48 + lVar1 + 0x32);
        if (lVar8 != -1) {
          *(undefined1 *)(param_3 + lVar8 * 8) = 1;
          local_40[0] = FUN_0028b340(param_1,(long)plVar3 + (long)sVar5 * 0x48 + lVar1 + 0x18);
          uVar2 = FUN_00057e60(local_40);
          *(undefined4 *)(param_3 + 4 + lVar8 * 8) = uVar2;
        }
        iVar6 = sVar5 + 1;
      } while ((int)(short)iVar6 < *piVar4);
    }
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

