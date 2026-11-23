
void FUN_0028e0c0(long param_1,long param_2,long param_3,long param_4)

{
  long *plVar1;
  int *piVar2;
  int *piVar3;
  short sVar4;
  char cVar6;
  undefined4 uVar7;
  long lVar5;
  
  thunk_FUN_012aa986(param_4,0,0x4000);
  plVar1 = (long *)FUN_0025a550();
  piVar2 = (int *)(**(code **)(*plVar1 + 0x2b8))(plVar1);
  plVar1 = (long *)FUN_0025a550();
  piVar3 = (int *)(**(code **)(*plVar1 + 0x2d0))(plVar1);
  if (0 < *piVar2) {
    sVar4 = 0;
    do {
      lVar5 = (long)sVar4;
      cVar6 = *(char *)(param_3 + lVar5);
      if ((cVar6 == '\0') && (cVar6 = *(char *)(param_2 + lVar5), cVar6 == '\0')) {
        cVar6 = *(char *)(param_1 + lVar5);
      }
      *(char *)(param_4 + lVar5) = cVar6;
      sVar4 = sVar4 + 1;
    } while ((int)sVar4 < *piVar2);
  }
  if (0 < *piVar3) {
    sVar4 = 0;
    do {
      lVar5 = (long)sVar4;
      if (*(char *)(param_3 + 0x2000 + lVar5 * 8) == '\0') {
        if (*(char *)(param_2 + 0x2000 + lVar5 * 8) == '\0') {
          uVar7 = *(undefined4 *)(param_1 + 0x2004 + lVar5 * 8);
        }
        else {
          uVar7 = *(undefined4 *)(param_2 + 0x2004 + lVar5 * 8);
        }
      }
      else {
        uVar7 = *(undefined4 *)(param_3 + 0x2004 + lVar5 * 8);
      }
      *(undefined4 *)(param_4 + 0x2000 + lVar5 * 4) = uVar7;
      sVar4 = sVar4 + 1;
    } while ((int)sVar4 < *piVar3);
  }
  return;
}

