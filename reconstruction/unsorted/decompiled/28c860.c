
void FUN_0028c860(long param_1,undefined8 param_2,long param_3)

{
  char cVar1;
  short sVar2;
  int iVar3;
  long *plVar4;
  int *piVar5;
  long *plVar6;
  long lVar7;
  long lVar8;
  undefined4 *puVar9;
  int iVar10;
  int iVar11;
  int local_250 [2];
  undefined4 local_248 [132];
  long local_38;
  
  local_38 = *DAT_01a1f100;
  plVar4 = (long *)FUN_0025a550();
  piVar5 = (int *)(**(code **)(*plVar4 + 0x290))(plVar4);
  if ((piVar5 != (int *)0x0) && (0 < *piVar5)) {
    lVar7 = 0;
    do {
      *(undefined1 *)(param_3 + *(short *)((long)piVar5 + lVar7 * 8 + *(long *)(piVar5 + 2) + 0x1c))
           = *(undefined1 *)(param_1 + 0x383c + lVar7);
      lVar7 = lVar7 + 1;
    } while ((int)lVar7 < *piVar5);
  }
  plVar4 = (long *)FUN_0025a550();
  piVar5 = (int *)(**(code **)(*plVar4 + 0x2c0))(plVar4);
  if ((piVar5 != (int *)0x0) && (0 < *piVar5)) {
    lVar7 = 0;
    do {
      lVar8 = (long)*(short *)((long)piVar5 + lVar7 * 8 + *(long *)(piVar5 + 2) + 0x1c);
      *(undefined1 *)(param_3 + 0x2000 + lVar8 * 8) = 1;
      *(undefined4 *)(param_3 + 0x2004 + lVar8 * 8) = *(undefined4 *)(param_1 + 0x4458 + lVar7 * 4);
      lVar7 = lVar7 + 1;
    } while ((int)lVar7 < *piVar5);
  }
  plVar4 = (long *)FUN_0025a550();
  local_250[0] = 0;
  FUN_00264c00(param_1,param_2,local_250);
  if (0 < local_250[0]) {
    iVar11 = 0;
    puVar9 = local_248;
    do {
      lVar7 = (**(code **)(*plVar4 + 0x358))(plVar4,*puVar9);
      if ((long)*(short *)(lVar7 + 4) != -1) {
        *(undefined1 *)(param_3 + *(short *)(lVar7 + 4)) = 2;
      }
      sVar2 = *(short *)(lVar7 + 6);
      lVar7 = (long)sVar2;
      if (lVar7 != -1) {
        if (*(char *)(param_3 + 0x2000 + lVar7 * 8) == '\0') {
          *(undefined1 *)(param_3 + 0x2000 + lVar7 * 8) = 1;
          *(undefined4 *)(param_3 + 0x2004 + lVar7 * 8) = 1;
        }
        else {
          iVar3 = *(int *)(param_3 + 0x2004 + lVar7 * 8);
          plVar6 = (long *)FUN_0025a550();
          lVar8 = (**(code **)(*plVar6 + 0x538))(plVar6,(int)sVar2);
          cVar1 = *(char *)(lVar8 + 5);
          if (cVar1 == '\x01') {
            iVar10 = 1;
            if (iVar3 < 2) goto LAB_0028ca30;
          }
          else if (cVar1 == '\x03') {
            iVar10 = iVar3 + 1;
          }
          else if ((cVar1 != '\x02') || (iVar10 = 1, 0 < iVar3)) goto LAB_0028ca30;
          *(int *)(param_3 + 0x2004 + lVar7 * 8) = iVar10;
        }
      }
LAB_0028ca30:
      puVar9 = puVar9 + 4;
      iVar11 = iVar11 + 1;
    } while (iVar11 < local_250[0]);
  }
  if (*DAT_01a1f100 != local_38) {
    thunk_FUN_012aa7f6();
    return;
  }
  return;
}

